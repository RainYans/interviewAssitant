# test_api.py - API测试脚本
import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

def test_api():
    """测试API接口"""
    print("🔄 开始测试API接口...")
    
    # 1. 测试健康检查
    print("\n1. 测试健康检查")
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"状态: {response.status_code}")
        print(f"响应: {response.json()}")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return
    
    # 2. 测试注册
    print("\n2. 测试用户注册")
    register_data = {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "123456"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=register_data)
        print(f"状态: {response.status_code}")
        if response.status_code == 200:
            print(f"响应: {response.json()}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"❌ 注册测试失败: {e}")
    
    # 3. 测试登录
    print("\n3. 测试用户登录")
    login_data = {
        "username": "test",  # 使用默认测试用户
        "password": "123456"
    }
    
    token = None
    try:
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        print(f"状态: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"响应: {result}")
            token = result.get("token")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"❌ 登录测试失败: {e}")
    
    if not token:
        print("❌ 无法获取token，停止后续测试")
        return
    
    # 4. 测试获取用户信息
    print("\n4. 测试获取用户信息")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        print(f"状态: {response.status_code}")
        if response.status_code == 200:
            print(f"响应: {response.json()}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"❌ 获取用户信息失败: {e}")
    
    # 5. 测试获取用户资料
    print("\n5. 测试获取用户资料")
    try:
        response = requests.get(f"{BASE_URL}/users/profile", headers=headers)
        print(f"状态: {response.status_code}")
        if response.status_code == 200:
            print(f"响应: {response.json()}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"❌ 获取用户资料失败: {e}")
    
    # 6. 测试更新用户资料
    print("\n6. 测试更新用户资料")
    profile_data = {
        "age": 23,
        "graduationYear": "2025",
        "education": "硕士",
        "school": "测试大学",
        "majorCategory": "computer",
        "major": "软件工程",
        "targetPosition": ["技术开发", "算法工程师"]
    }
    
    try:
        response = requests.put(f"{BASE_URL}/users/profile", json=profile_data, headers=headers)
        print(f"状态: {response.status_code}")
        if response.status_code == 200:
            print(f"响应: {response.json()}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"❌ 更新用户资料失败: {e}")
    
    print("\n✅ API测试完成")

if __name__ == "__main__":
    test_api()