#预测
from core_utils.dict_to_str import *
from services.load_person import load_persona_md


def production_prediction(input_data):
    """
    生产预测
    """
    system_prompt = load_persona_md("person/yuce.md")
    system_set = """
        结合数据，预测未来一个月的数据，将数据填入[待填入]
        预测数值必须为整数不能为浮点数
        要求格式[待填入]直接变成整数，只输出下面填充完的格式，不输出多余元素
品牌A_装配工序,品牌A_成品Z,[待填入]
品牌A_装配工序,品牌A_损耗,[待填入]
品牌B_损耗,总损耗,[待填入]
原材料A,品牌A_预处理工序,[待填入]
品牌A_加工工序,品牌A_半成品X,[待填入]
品牌A_加工工序,品牌A_半成品Y,[待填入]
品牌A_加工工序,品牌A_损耗,[待填入]
品牌A_半成品Y,品牌A_装配工序,[待填入]
品牌A_半成品Y,品牌A_损耗,[待填入]
品牌B_半成品Y,品牌B_装配工序,[待填入]
品牌B_半成品Y,品牌B_损耗,[待填入]
品牌B_加工工序,品牌B_半成品X,[待填入]
品牌B_加工工序,品牌B_半成品Y,[待填入]
品牌B_加工工序,品牌B_损耗,[待填入]
原材料E,品牌B_预处理工序,[待填入]
原材料D,品牌A_预处理工序,[待填入]
品牌A_成品Z,总损耗,[待填入]
品牌B_成品Z,总损耗,[待填入]
品牌A_半成品X,品牌A_装配工序,[待填入]
品牌A_半成品X,品牌A_损耗,[待填入]
品牌B_半成品X,品牌B_装配工序,[待填入]
品牌B_半成品X,品牌B_损耗,[待填入]
品牌B_预处理工序,品牌B_加工工序,[待填入]
品牌B_预处理工序,品牌B_损耗,[待填入]
原材料B,品牌B_预处理工序,[待填入]
原材料C,品牌A_预处理工序,[待填入]
原材料C,品牌B_预处理工序,[待填入]
品牌A_预处理工序,品牌A_加工工序,[待填入]
品牌A_预处理工序,品牌A_损耗,[待填入]
品牌B_装配工序,品牌B_成品Z,[待填入]
品牌B_装配工序,品牌B_损耗,[待填入]
品牌A_损耗,总损耗,[待填入]
    """
    user_prompt = production_to_string(input_data)
    prompt = f"\n\n用户：{user_prompt}{system_set}\n\n"
    return prompt,system_prompt

def sales_prediction(input_data):
    system_prompt = load_persona_md("person/yuce.md")
    system_set = """
    你是一个专业的新能源预测模型，你的任务是根据输入的新能源数据，预测未来一个月的销售走势。
    """
    user_prompt = sales_to_string(input_data)
    prompt = f"{system_set}\n\n用户：{user_prompt}\n\n"
    return prompt,system_prompt