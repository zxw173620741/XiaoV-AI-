from services.load_person import load_persona_md


def production_analysis(input_data):
    """
    生产分析
    """
    system_prompt = load_persona_md("person/fenxi.md")
    system_set = """
        根据数据，生成以下格式：
        问题发现：
            A品牌:不超过五条
            B品牌:不超过五条
        解决措施：
            A品牌:不超过三条
            B品牌:不超过三条
        最终结论：
            A品牌:不超过五句话
            B品牌:不超过五句话
    """
    user_prompt = input_data
    prompt = f"{system_set}\n\n用户：{user_prompt}\n\n"
    return prompt,system_prompt

def Car_evaluation_analysis(input_data):
    """
    汽车评价分析
    """
    system_prompt = load_persona_md("person/fenxi.md")
    system_set = """
        根据数据，生成以下格式：
        问题发现：
            A品牌:不超过五条
            B品牌:不超过五条
        解决措施：
            A品牌:不超过三条
            B品牌:不超过三条
        最终结论：
            A品牌:不超过五句话
            B品牌:不超过五句话
    """
    user_prompt = input_data
    prompt = f"{system_set}\n\n用户：{user_prompt}\n\n"
    return prompt,system_prompt

def Production_Problems_analysis(input_data):
    """
    生产问题分析
    """
    system_prompt = load_persona_md("person/fenxi.md")
    system_set = """
        根据数据，生成以下格式：
        问题发现：
            A品牌:不超过五条
            B品牌:不超过五条
        解决措施：
            A品牌:不超过三条
            B品牌:不超过三条
        最终结论：
            A品牌:不超过五句话
            B品牌:不超过五句话
    """
    user_prompt = input_data
    prompt = f"{system_set}\n\n用户：{user_prompt}\n\n"
    return prompt,system_prompt