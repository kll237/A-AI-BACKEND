import requests
import json


def test_all_endpoints():
    base_url = "http://localhost:8000/api/v1"

    print("🔍 详细测试API端点")
    print("=" * 70)

    endpoints = [
        # 摄像头相关
        ("GET", "/cameras", "获取所有摄像头"),
        ("POST", "/cameras", "创建摄像头"),
        ("GET", "/cameras/with-filters", "获取带过滤器的摄像头"),
        ("GET", "/contextual/cameras", "获取上下文摄像头"),

        # 过滤器相关
        ("GET", "/filters", "获取所有过滤器"),

        # 用户相关
        ("GET", "/users", "获取所有用户"),

        # 分析相关
        ("GET", "/analysis/status", "获取分析状态"),
        ("POST", "/analysis/start", "开始分析"),
        ("POST", "/analysis/stop", "停止分析"),
    ]

    for method, endpoint, description in endpoints:
        url = base_url + endpoint

        try:
            print(f"\n📡 {description}:")
            print(f"   URL: {method} {endpoint}")

            if method == "GET":
                response = requests.get(url, timeout=5)
            elif method == "POST":
                # 对于POST请求，发送最小化的数据
                if endpoint == "/cameras":
                    data = {"name": "test", "rtsp_url": "test"}
                elif "analysis" in endpoint:
                    data = {}
                else:
                    data = {}
                response = requests.post(url, json=data, timeout=5)

            print(f"   状态码: {response.status_code}")

            if response.status_code == 200:
                print("   ✅ 成功")
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"   返回 {len(data)} 项数据")
                    elif isinstance(data, dict):
                        print(f"   返回字典，包含 {len(data)} 个键")
                except:
                    print(f"   返回: {response.text[:100]}...")
            elif response.status_code == 500:
                print("   ❌ 服务器错误 (500)")
                print(f"   错误: {response.text[:200]}")
            else:
                print(f"   ⚠️  其他状态码")

        except Exception as e:
            print(f"   ❌ 请求失败: {e}")


def check_frontend_access():
    """检查前端可能访问的端点"""
    print("\n" + "=" * 70)
    print("🔗 前端连接检查")
    print("=" * 70)

    # 模拟前端请求
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    frontend_endpoints = [
        "/api/v1/contextual/cameras",  # 前端主要访问的端点
        "/api/v1/cameras/with-filters",
        "/api/v1/filters",
    ]

    for endpoint in frontend_endpoints:
        url = "http://localhost:8000" + endpoint
        try:
            response = requests.get(url, headers=headers, timeout=5)
            print(f"\n🌐 {endpoint}:")
            print(f"   状态: {response.status_code}")

            if response.status_code == 500:
                # 尝试获取详细错误
                print("   ❌ 前端访问失败 - 服务器错误")
                error_detail = response.text
                if "gbk" in error_detail.lower() or "编码" in error_detail.lower():
                    print("   🔧 问题: 编码错误 (GBK/UTF-8问题)")
                print(f"   错误详情: {error_detail[:300]}")
            elif response.status_code == 200:
                print("   ✅ 前端可正常访问")

        except Exception as e:
            print(f"\n🌐 {endpoint}:")
            print(f"   ❌ 请求异常: {e}")


if __name__ == "__main__":
    test_all_endpoints()
    check_frontend_access()