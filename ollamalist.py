import requests

# 远程 Ollama 服务地址（修改为你远程服务器的 IP 或域名）
OLLAMA_HOST = "http://192.168.201.11:11434"  

def list_models():
    """获取远程 Ollama 上的模型列表"""
    url = f"{OLLAMA_HOST}/api/tags"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        print("可用模型：")
        for m in data.get("models", []):
            print(f"- {m['name']} (size: {m.get('size', '未知')})")
    except Exception as e:
        print("获取模型列表失败：", e)

def run_model(model: str, prompt: str):
    """调用远程 Ollama 模型"""
    url = f"{OLLAMA_HOST}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False  # 设置为 True 可以流式返回
    }
    try:
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        print("模型回复：")
        print(data.get("response", "无响应"))
    except Exception as e:
        print("调用模型失败：", e)


if __name__ == "__main__":
    # 1. 查看有哪些模型
    list_models()
