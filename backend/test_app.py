import requests

def test_app():
    # 测试根路由
    response = requests.get('http://127.0.0.1:5000/')
    print(f"根路由状态码: {response.status_code}")
    
    # 测试API路由
    response = requests.get('http://127.0.0.1:5000/api/posts')
    print(f"API路由状态码: {response.status_code}")
    print(f"API响应: {response.json() if response.status_code == 200 else 'N/A'}")
    
    # 测试测试路由
    response = requests.get('http://127.0.0.1:5000/test')
    print(f"测试路由状态码: {response.status_code}")
    print(f"测试响应: {response.text}")

if __name__ == "__main__":
    test_app() 