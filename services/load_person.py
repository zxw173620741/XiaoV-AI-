def load_persona_md(file_path="persona.md") -> str:
    """读取Markdown人设文件并返回字符串"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"错误：人设文件 {file_path} 不存在")
        return ""
    except Exception as e:
        print(f"读取人设文件失败: {e}")
        return ""