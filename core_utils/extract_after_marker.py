def extract_after_marker(text: str, marker: str = '</think>') -> str:
    """
    提取标记之后的字符串内容
    参数:
        text: 要处理的原始字符串
        marker: 用于定位的标记字符串，默认为'</think>'
    返回:
        标记之后的字符串，如果标记不存在则返回空字符串
    """
    # 查找标记的位置
    marker_index = text.find(marker)
    
    # 如果找到标记，返回标记后面的内容；否则返回空字符串
    if marker_index != -1:
        # 计算标记结束后的起始位置（标记长度 + 标记起始索引）
        start_index = marker_index + len(marker)
        return text[start_index:]
    return ""
