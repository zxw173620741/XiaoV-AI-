import requests


def production_to_string(json_data):
    """
    将JSON数据转换为指定格式的字符串
    
    参数:
        json_data: 原始JSON数据（列表套字典，含source/target/value/month）
        
    返回:
        str: 按日期分组的字符串，格式为"年-月,来源,目标,整数值"
    """
    from collections import defaultdict
    
    # 按月份分组数据
    month_groups = defaultdict(list)
    for item in json_data:
        month = item["month"]
        source = item["source"]
        target = item["target"]
        value = int(float(item["value"]))  # 去除小数
        month_groups[month].append(f"{month},{source},{target},{value}")
    
    # 按月份排序并拼接结果
    sorted_months = sorted(month_groups.keys())
    result = []
    for month in sorted_months:
        result.extend(month_groups[month])
        result.append("")  # 月份间加空行
    
    return "\n".join(result).strip()

def sales_to_string(json_data):
    """
    将销售JSON数据转换为指定格式的字符串
    
    参数:
        json_data: 原始销售数据（列表套字典，含brand/region/plannedSales/actualSales/month）
        
    返回:
        str: 按日期分组的字符串，格式为"年-月,品牌,地区,计划销售额,实际销售额"
    """
    from collections import defaultdict
    
    # 按月份分组数据
    month_groups = defaultdict(list)
    for item in json_data:
        month = item["month"]
        brand = item["brand"]
        region = item["region"]
        planned = int(float(item["plannedSales"]))  # 去除小数
        actual = int(float(item["actualSales"]))    # 去除小数
        month_groups[month].append(f"{month},{brand},{region},{planned},{actual}")
    
    # 按月份排序并拼接结果
    sorted_months = sorted(month_groups.keys())
    result = []
    for month in sorted_months:
        result.extend(month_groups[month])
        result.append("")  # 月份间加空行
    
    return "\n".join(result).strip()
# 使用示例
if __name__ == "__main__":
    # 模拟输入（与原问题结构相同）
    input_data = requests.get('http://154.219.112.111:8089/api/ads-ai-production').json()
    input_data1 = requests.get('http://154.219.112.111:8089/api/ads-ai-sales').json()
    # 调用函数并打印
    output_str =sales_to_string(input_data1)
    print(output_str)