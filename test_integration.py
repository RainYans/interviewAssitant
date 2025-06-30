#!/usr/bin/env python3
# test_integration.py - 前后端对接测试

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_register():
    """测试注册功能"""
    print("🔄 测试用户注册...")
    
    # 模拟前端发送的注册数据
    register_data = {
        "username": "frontend_test",
        "email": "frontend_test@example.com", 
        "password": "123456"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=register_data)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 注册成功: {result}")
            return True
        else:
            print(f"❌ 注册失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_login():
    """测试登录功能"""
    print("\n🔄 测试用户登录...")
    
    # 模拟前端发送的登录数据（与前端Login.vue格式一致）
    login_data = {
        "username": "test",  # 可以是邮箱或用户名
        "password": "123456"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 登录成功:")
            print(f"   Token: {result['token'][:50]}...")
            print(f"   User: {result['user']}")
            return result['token']
        else:
            print(f"❌ 登录失败: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None

def test_user_profile(token):
    """测试用户资料API"""
    print("\n🔄 测试用户资料...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # 测试获取用户基本信息
        response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ 获取用户信息: {user_info}")
        else:
            print(f"❌ 获取用户信息失败: {response.text}")
            return False
        
        # 测试获取用户资料（适配前端Profile.vue）
        response = requests.get(f"{BASE_URL}/users/profile", headers=headers)
        if response.status_code == 200:
            profile = response.json()
            print(f"✅ 获取用户资料: {profile}")
        else:
            print(f"❌ 获取用户资料失败: {response.text}")
        
        # 测试更新用户资料（模拟前端Profile.vue提交的数据）
        profile_data = {
            "age": 23,
            "graduationYear": "2024",
            "education": "本科",
            "school": "测试大学",
            "majorCategory": "computer",
            "major": "计算机科学与技术",
            "targetPosition": ["技术开发", "产品经理"]
        }
        
        response = requests.put(f"{BASE_URL}/users/profile", json=profile_data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 更新用户资料: {result}")
        else:
            print(f"❌ 更新用户资料失败: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_cors():
    """测试CORS设置"""
    print("\n🔄 测试CORS设置...")
    
    headers = {
        "Origin": "http://localhost:3000",  # 前端开发服务器地址
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type"
    }
    
    try:
        # 发送预检请求
        response = requests.options(f"{BASE_URL}/login", headers=headers)
        print(f"OPTIONS请求状态码: {response.status_code}")
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
        }
        
        print(f"CORS Headers: {cors_headers}")
        
        if cors_headers['Access-Control-Allow-Origin']:
            print("✅ CORS设置正常")
            return True
        else:
            print("❌ CORS设置可能有问题")
            return False
            
    except Exception as e:
        print(f"❌ CORS测试异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始前后端对接测试...\n")
    
    # 1. 测试注册
    register_success = test_register()
    
    # 2. 测试登录
    token = test_login()
    
    # 3. 如果登录成功，测试用户资料API
    if token:
        test_user_profile(token)
    
    # 4. 测试CORS
    test_cors()
    
    print("\n" + "="*60)
    
    if register_success or token:  # 注册或登录任意一个成功即可
        print("🎉 前后端对接测试基本通过！")
        print("\n📝 前端配置检查清单:")
        print("1. 确保前端环境变量设置正确:")
        print("   VITE_API_BASE_URL=http://localhost:8000/api/v1")
        print("\n2. 启动前端开发服务器:")
        print("   npm run dev")
        print("\n3. 使用测试账号登录:")
        print("   用户名: test")
        print("   密码: 123456")
        print("\n4. 或者注册新账号测试完整流程")
        
    else:
        print("❌ 前后端对接存在问题，请检查:")
        print("1. 后端服务是否正常运行在 localhost:8000")
        print("2. 数据库连接是否正常")
        print("3. 是否有语法错误或导入问题")

if __name__ == "__main__":
    main()