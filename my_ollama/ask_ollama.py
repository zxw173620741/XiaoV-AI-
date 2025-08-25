import requests
import os
from dotenv import load_dotenv

load_dotenv()

#ollama函数，提供字符串用户询问词
def ask_ollama(prompt,renshe):
    api_url = os.getenv("OLLAMA_API_URL")
    payload = {
        "model": os.getenv("OLLAMA_MODEL"),         # 指定模型
        "system": renshe,#系统人设
        # "prompt": os.getenv("OLLAMA_PROMPT"),       # 用户问题
        "prompt":prompt,
        "stream": True,     # 是否流式输出
        "options": {              
            "temperature": 0.5,
            "max_tokens": 20000
        }
    }
    print(renshe)
    print(prompt)
    try:
        with ( 
            requests.post(
            api_url,
            json=payload,  # 自动序列化为JSON
            headers={"Content-Type": "application/json"},
            stream=True,)
        as response):
            response.raise_for_status()  # 如果响应状态码不是200，将抛出HTTPError
            for line in response.iter_lines():
                if line:
                        yield line.decode('utf-8') + '\n'

        
    except requests.exceptions.RequestException as e:
        print(f"请求发生错误: {e}")
        return None
    except ValueError as e:
        print(f"响应JSON解析错误: {e}")
        return None