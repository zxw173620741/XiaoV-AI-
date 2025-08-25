from typing import Dict, List, TypedDict
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END
from ollama import *
import re
import traceback
import json
import os
import time
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()
api_url = os.getenv("OLLAMA_URL")
# 定义状态结构
class AgentState(TypedDict):
    problem:str
    reasons:List[str]
    knowledge:Dict[str,Dict[str,str]]
    model_advice:Dict[str,str]


class StringOutputLogger:
    def __init__(self):
        self.output_buffer = []
    
    def step_start(self, msg):
        self.output_buffer.append(f"\n{'=' * 50}")
        self.output_buffer.append(f"🚀 {msg}")
        self.output_buffer.append(f"{'=' * 50}")
    
    def step_info(self, msg):
        self.output_buffer.append(f"ℹ️ {msg}")
    
    def step_success(self, msg):
        self.output_buffer.append(f"✅ {msg}")
    
    def step_warning(self, msg):
        self.output_buffer.append(f"⚠️ {msg}")
    
    def show_state(self, state):
        self.output_buffer.append("\n当前状态:")
        for key, value in state.items():
            if key == "knowledge" or key == "model_advice":
                self.output_buffer.append(f"  {key}:")
                for subkey, subvalue in value.items():
                    self.output_buffer.append(f"    {subkey}: {str(subvalue)[:80]}...")
            else:
                self.output_buffer.append(f"  {key}: {value}")
    
    def get_output(self):
        return "\n".join(self.output_buffer)
    
    def clear(self):
        self.output_buffer = []


# 替换原来的VisualLogger
logger = StringOutputLogger()


# 知识库查询函数（从文本文件读取）
def query_knowledge_base(problem: str, reason: str) -> dict:
    """从文本文件查询知识库"""
    logger.step_info(f"查询知识库: 问题={problem}, 异常指标={reason}")

    # 默认返回结果
    default_result = {"solution": "暂无方案", "case": "无相关案例"}

    # 知识库文件路径 - 根据您的实际位置调整
    knowledge_file = "knowledge_base/sales_knowledge"

    # 检查文件是否存在
    if not os.path.exists(knowledge_file):
        logger.step_warning(f"知识库文件 {knowledge_file} 不存在")
        return default_result

    try:
        # 读取整个文件内容
        with open(knowledge_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 将内容分割为不同原因的部分
        sections = content.strip().split("\n\n")

        # 解析每个部分
        for section in sections:
            lines = section.strip().split("\n")
            if not lines:
                continue

            # 第一行是原因名称
            section_reason = lines[0].strip()
            if section_reason != reason:
                continue

            # 解析解决方案和案例
            solution_lines = []
            case_lines = []
            current_section = None

            for line in lines[1:]:
                if line.startswith("解决方案:"):
                    current_section = "solution"
                    continue
                elif line.startswith("案例:"):
                    current_section = "case"
                    continue

                if current_section == "solution":
                    solution_lines.append(line.strip())
                elif current_section == "case":
                    case_lines.append(line.strip())

            # 构建结果
            result = {
                "solution": "\n".join(solution_lines),
                "case": " ".join(case_lines)
            }

            logger.step_info(f"知识库返回结果: {result}")
            return result

        # 如果没找到匹配的原因
        logger.step_warning(f"未找到原因 '{reason}' 的解决方案")
        return default_result

    except Exception as e:
        logger.step_warning(f"读取知识库文件出错: {str(e)}")
        return default_result


# 调用大模型生成建议
def generate_model_advice(problem: str, reason: str, knowledge: dict) -> dict:
    """使用Ollama大模型生成建议和案例总结"""
    logger.step_info(f"调用大模型处理: 问题={problem}, 原因={reason}")

    # 构造更清晰的提示词
    prompt = f"""
    你是一个资深生产管理顾问。请基于以下信息为问题提供专业建议：

    **核心问题**: {problem}
    **具体原因**: {reason}

    **知识库解决方案**:
    {knowledge['solution']}

    **知识库典型案例**:
    {knowledge['case']}

    请参考案例生成对该原因的专业建议,300字以内：
    请使用以下格式:
    <建议开始>
    你的建议内容...
    <建议结束>

    """

    try:
        # 调用Ollama模型
        logger.step_info("发送提示词给模型...")
        client = Client(host=api_url)
        response = client.chat(
            model='deepseek-r1:8b',
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0.3, 'num_ctx': 4096}
        )

        # 获取模型响应
        output = response['message']['content']

        advice = ""

        # 尝试使用正则表达式提取内容
        advice_match = re.search(r'<建议开始>([\s\S]*?)<建议结束>', output)

        if advice_match:
            advice = advice_match.group(1).strip()
        else:
            logger.step_warning("未找到建议部分标记")
            # 尝试提取第一部分内容作为建议
            if "建议" in output or "方案" in output:
                advice = output.split("\n\n")[0].strip()
            else:
                advice = "未能提取建议内容"

        return {"advice": advice}

    except Exception as e:
        logger.step_warning(f"模型调用出错: {str(e)}")
        return {"advice": "模型调用出错", "summary": "请检查模型服务"}


# 定义节点函数
def process_reason(state: AgentState, config: RunnableConfig) -> AgentState:
    print(f"\n{'=' * 50}")
    print(f"开始分析异常指标: {state['reasons'][0]}")
    reason=state['reasons'][0]
    knowledge=query_knowledge_base(state['problem'],reason)
    model_output=generate_model_advice(state['problem'],reason,knowledge)
    new_state={
        'problem':state['problem'],
        'reasons':state['reasons'][1:],
        'knowledge':{**state['knowledge'],reason:knowledge},
        'model_advice':{**state['model_advice'],reason:model_output['advice']}
    }
    print(f"异常指标{reason}已经分析完成")
    return new_state



def should_continue(state: AgentState) -> str:
    continue_flag = "continue" if state["reasons"] else "end"
    return continue_flag


# 创建工作流
def create_workflow():
    workflow=StateGraph(AgentState)
    workflow.add_node("process_reason",process_reason)
    workflow.add_conditional_edges(
        "process_reason",
        should_continue,{
            "continue":"process_reason",
            "end":END
        }
    )
    workflow.set_entry_point("process_reason")
    return workflow.compile()

# 最终结果可视化
def visualize_final_result(final_state):
    result_lines = []
    result_lines.append("\n" + "=" * 50)
    result_lines.append("✨ 最终问题分析报告 ✨")
    result_lines.append("=" * 50)

    result_lines.append(f"\n核心问题: {final_state['problem']}")

    for reason in final_state['knowledge'].keys():
        result_lines.append("\n" + "=" * 30 + f" 异常指标: {reason} " + "=" * 30)

        # 知识库解决方案
        result_lines.append("\n📚 知识库解决方案:")
        result_lines.append(final_state['knowledge'][reason]['solution'])

        # 模型建议
        result_lines.append("\n💡 大模型建议:")
        result_lines.append(final_state['model_advice'][reason])

        # 案例参考
        result_lines.append("\n🔍 相关案例参考:")
        result_lines.append(final_state['knowledge'][reason]['case'])

    return "\n".join(result_lines)


def analyze_problem(problem: str, reasons: List[str]) -> Dict:
    """
    执行完整的工作流分析
    
    参数:
        problem: 核心问题描述
        reasons: 需要分析的异常指标列表
        
    返回:
        {
            "result": 分析结果字典,
            "log": 完整的执行日志,
            "report": 格式化报告
        }
    """
    print("工作流服务已经启动")
    logger.clear()
    try:
        logger.step_start("启动工作流")
        
        # 记录开始时间
        start_time = time.time()
        
        # 初始化输入状态
        initial_state: AgentState = {
            "problem": problem,
            "reasons": reasons,
            "knowledge": {},
            "model_advice": {}
        }

        logger.step_info(f"初始问题: {initial_state['problem']}")
        logger.step_info(f"待分析异常指标: {', '.join(initial_state['reasons'])}")

        # 创建并执行工作流
        workflow = create_workflow()
        logger.step_info("工作流创建完成，开始执行...")

        # 执行工作流
        final_state = workflow.invoke(initial_state)

        # 生成报告
        report = visualize_final_result(final_state)

        # 计算执行时间
        execution_time = round(time.time() - start_time, 2)
        
        # 构造返回结果
        result = {
            "problem": final_state["problem"],
            "knowledge": final_state["knowledge"],
            "model_advice": final_state["model_advice"],
            "status": "success",
            "execution_time": f"{execution_time}秒",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }
        
        logger.step_success(f"工作流执行完成！耗时{execution_time}秒")
        
        return {
            "result": result,
            "log": logger.get_output(),
            "report": report
        }
        
    except Exception as e:
        error_msg = f"工作流执行失败: {str(e)}"
        logger.step_warning(error_msg)
        
        return {
            "result": {
                "problem": problem,
                "knowledge": {},
                "model_advice": {},
                "status": "error",
                "error": error_msg,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            },
            "log": logger.get_output(),
            "report": "分析过程中出现错误"
        }


# 使用示例
if __name__ == "__main__":
    # 示例调用
    analysis_result = analyze_problem(
        "production_efficiency",
        ["inventory_turnover_rate", "work_hours", "defect_rate", "completion_rate"]
    )
    
    # 打印日志
    print(analysis_result["log"])
    
    # 打印报告
    print(analysis_result["report"])
    
    # 访问结果数据
    print("\n分析结果数据:")
    print(json.dumps(analysis_result["result"], indent=2, ensure_ascii=False))