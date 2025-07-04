# app/api/resumes.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
from datetime import datetime

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.resume import Resume
from app.core.config import settings

# 创建路由器
router = APIRouter()

# 允许的文件类型
ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename: str) -> bool:
    """检查文件类型是否允许"""
    return '.' in filename and \
           os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS

def get_file_size(file: UploadFile) -> int:
    """获取上传文件大小"""
    file.file.seek(0, 2)  # 移动到文件末尾
    size = file.file.tell()  # 获取当前位置（即文件大小）
    file.file.seek(0)  # 重置到文件开头
    return size

@router.post("/")
async def upload_resume(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    上传简历
    POST /api/v1/resumes
    """
    try:
        # 验证文件
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="没有选择文件"
            )
        
        if not allowed_file(file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不支持的文件类型，只支持 PDF、DOC、DOCX 格式"
            )
        
        # 检查文件大小
        file_size = get_file_size(file)
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件太大，最大支持10MB"
            )
        
        # 生成唯一文件名
        file_ext = os.path.splitext(file.filename)[1].lower()
        stored_filename = f"{uuid.uuid4().hex}{file_ext}"
        
        # 确保上传目录存在
        upload_dir = "uploads/resumes"
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(upload_dir, stored_filename)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 创建数据库记录
        resume = Resume(
            user_id=current_user.id,
            filename=file.filename,
            stored_filename=stored_filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file_ext[1:],  # 去掉点号
            is_active=False  # 默认不激活
        )
        
        db.add(resume)
        db.commit()
        db.refresh(resume)
        
        print(f" 用户 {current_user.username} 上传简历成功: {file.filename}")
        
        return {
            "code": 200,
            "data": {
                "id": resume.id,
                "filename": resume.filename,
                "file_size": resume.file_size,
                "file_type": resume.file_type,
                "upload_time": resume.created_at.isoformat(),
                "is_active": resume.is_active
            },
            "message": "简历上传成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"简历上传失败: {str(e)}")
        # 如果出错，删除已保存的文件
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传失败: {str(e)}"
        )

@router.get("/")
def get_resumes(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户的简历列表
    GET /api/v1/resumes
    """
    try:
        resumes = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).all()
        
        resume_list = []
        for resume in resumes:
            resume_data = {
                "id": resume.id,
                "filename": resume.filename,
                "stored_filename": resume.stored_filename,  # 添加这行
                "file_size": resume.file_size,
                "file_type": resume.file_type,
                "upload_time": resume.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "is_active": resume.is_active,
                "is_parsed": resume.is_parsed
            }
            
            # 如果有解析数据，添加到响应中
            if resume.parsed_data:
                import json
                try:
                    resume_data["parsed"] = json.loads(resume.parsed_data)
                except:
                    pass
            
            resume_list.append(resume_data)
        
        return {
            "code": 200,
            "data": resume_list,
            "message": "获取简历列表成功"
        }
        
    except Exception as e:
        print(f"获取简历列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取简历列表失败: {str(e)}"
        )

@router.delete("/{resume_id}")
def delete_resume(
    resume_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除简历
    DELETE /api/v1/resumes/{resume_id}
    """
    try:
        # 查找简历
        resume = db.query(Resume).filter(
            Resume.id == resume_id,
            Resume.user_id == current_user.id
        ).first()
        
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="简历不存在"
            )
        
        # 删除文件
        if os.path.exists(resume.file_path):
            os.remove(resume.file_path)
        
        # 删除数据库记录
        db.delete(resume)
        db.commit()
        
        print(f"✅ 用户 {current_user.username} 删除简历: {resume.filename}")
        
        return {
            "code": 200,
            "data": {},
            "message": "简历删除成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"删除简历失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除简历失败: {str(e)}"
        )

@router.put("/{resume_id}/activate")
def set_active_resume(
    resume_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    设置默认简历
    PUT /api/v1/resumes/{resume_id}/activate
    """
    try:
        # 查找要激活的简历
        resume = db.query(Resume).filter(
            Resume.id == resume_id,
            Resume.user_id == current_user.id
        ).first()
        
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="简历不存在"
            )
        
        # 先取消所有简历的激活状态
        db.query(Resume).filter(Resume.user_id == current_user.id).update({"is_active": False})
        
        # 激活指定简历
        resume.is_active = True
        db.commit()
        
        print(f"用户 {current_user.username} 设置默认简历: {resume.filename}")
        
        return {
            "code": 200,
            "data": {"id": resume.id, "filename": resume.filename},
            "message": "默认简历设置成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"设置默认简历失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"设置默认简历失败: {str(e)}"
        )