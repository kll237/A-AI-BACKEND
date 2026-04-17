import sys
import os

# 设置路径
sys.path.insert(0, r"D:\jsjxm\A-AI-BACKEND")

try:
    print("正在导入模块...")
    from app.main import app
    import uvicorn

    print("=" * 50)
    print("🚀 启动AI摄像头系统")
    print("=" * 50)
    print("服务器: http://localhost:8001")
    print("文档: http://localhost:8001/docs")
    print("=" * 50)

    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)

except Exception as e:
    print(f"错误: {e}")
    import traceback

    traceback.print_exc()
    input("按Enter退出...")