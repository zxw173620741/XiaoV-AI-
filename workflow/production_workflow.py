from ast import mod
from pyexpat import model
import stat
from tkinter import W, Listbox
from turtle import st
from typing import Dict, List, TypedDict
from unittest import removeResult
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END
from ollama import *
import re
import traceback
import json
import os
import time
from tenacity import retry
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()
api_url = os.getenv("OLLAMA_URL")
class AgentState(TypedDict):
    problem:str
    reasons:List[str]
    knowledge:Dict[str,Dict[str,str]]
    model_advice:Dict[str,str]

class VisualLogger:
    @staticmethod
    def step_start(msg):
        print(f"\n\033[95m{'=' * 50}\033[0m")
        print(f"\033[95m🚀 {msg}\033[0m")
        print(f"\033[95m{'=' * 50}\033[0m")

    @staticmethod
    def step_info(msg):
        print(f"\033[94mℹ️ {msg}\033[0m")

    @staticmethod
    def step_success(msg):
        print(f"\033[92m✅ {msg}\033[0m")

    @staticmethod
    def step_warning(msg):
        print(f"\033[93m⚠️ {msg}\033[0m")

    @staticmethod
    def show_state(state):
        print("\n\033[96m当前状态:\033[0m")
        for key, value in state.items():
            if key == "knowledge" or key == "model_advice":
                print(f"  \033[93m{key}:\033[0m")
                for subkey, subvalue in value.items():
                    print(f"    \033[93m{subkey}:\033[0m {str(subvalue)[:80]}...")
            else:
                print(f"  \033[93m{key}:\033[0m {value}")

def query_knowledge_base(problem: str, reason: str) -> dict:
    """调用知识库进行查询"""
    VisualLogger.step_info(f"查询知识库: 问题={problem}, 异常指标={reason}")

    default_result = {"solution": "暂无方案", "case": "无相关案例"}

    knowledge_file = "knowledge_base/production_knowledge"

    if not os.path.exists(knowledge_file):
        VisualLogger.step_warning(f"知识库文件 {knowledge_file} 不存在")
        return default_result

    try:
        with open(knowledge_file, 'r', encoding='utf-8') as f:
            content = f.read()

        sections = content.strip().split("\n\n")

        for section in sections:
            lines = section.strip().split("\n")
            if not lines:
                continue

            section_reason = lines[0].strip()
            if section_reason != reason:
                continue

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

            result = {
                "solution": "\n".join(solution_lines),
                "case": " ".join(case_lines)
            }

            VisualLogger.step_info(f"知识库返回结果: {result}")
            return result

        VisualLogger.step_warning(f"未找到原因 '{reason}' 的解决方案")
        return default_result

    except Exception as e:
        VisualLogger.step_warning(f"读取知识库文件出错: {str(e)}")
        return default_result

def generate_model_advice(problem: str, reason: str, knowledge: dict) -> dict:
    """调用大模型分析问题"""
    VisualLogger.step_info(f"调用大模型处理: 问题={problem}, 原因={reason}")

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
        print("发送提示词给模型...")
        client = Client(host=api_url)
        response = client.chat(
            model='deepseek-r1:8b',
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0.3, 'num_ctx': 4096}
        )
        output = response['message']['content']

        advice = ""

        advice_match = re.search(r'<建议开始>([\s\S]*?)<建议结束>', output)

        if advice_match:
            advice = advice_match.group(1).strip()
        else:
            VisualLogger.step_warning("未找到建议部分标记")
            if "建议" in output or "方案" in output:
                advice = output.split("\n\n")[0].strip()
            else:
                advice = "未能提取建议内容"

        return {"advice": advice}

    except Exception as e:
        VisualLogger.step_warning(f"模型调用出错: {str(e)}")
        traceback.print_exc()
        return {"advice": "模型调用出错", "summary": "请检查模型服务"}

def process_reason(state: AgentState, config: RunnableConfig) -> AgentState:
    print(f"\n{'=' * 50}")
    print(f"开始分析异常指标: {state['reasons'][0]}")
    reason=state['reasons'][0]
    knowledge=query_knowledge_base(state['problem'],reason)
    model_output=generate_model_advice(state['problem'],reason,knowledge)
    new_state={
        "problem":state['problem'],
        "reasons":state['reasons'][1:],
        "knowledge":{**state["knowledge"],reason:knowledge},
        "model_advice":{**state['model_advice'],reason:model_output ['advice']}
    }
    print(f"针对异常指标{reason}分析完成")
    return new_state

def should_continue(state: AgentState) -> str:
    """判断异常指标是否处理完成"""
    continue_flag = "continue" if state["reasons"] else "end"
    return continue_flag

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

def visualize_final_result(final_state):
    print("\n\033[1;35m" + "=" * 50)
    print("✨ 最终问题分析报告 ✨")
    print("=" * 50 + "\033[0m")

    print(f"\n\033[1;34m核心问题: {final_state['problem']}\033[0m")

    for reason in final_state['knowledge'].keys():
        print("\n\033[1;32m" + "=" * 30 + f" 异常指标: {reason} " + "=" * 30 + "\033[0m")

        print("\n\033[93m📚 知识库解决方案:\033[0m")
        print(final_state['knowledge'][reason]['solution'])
        print("\n\033[96m💡 大模型建议:\033[0m")
        print(final_state['model_advice'][reason])
        print("\n\033[95m🔍 相关案例参考:\033[0m")
        print(final_state['knowledge'][reason]['case'])

if __name__ == "__main__":
    VisualLogger.step_start("启动工作流")
    initial_state: AgentState = {
        "problem": "production_efficiency",
        "reasons": ["inventory_turnover_rate", "work_hours", "defect_rate"],
        "knowledge": {},
        "model_advice": {}
    }

    VisualLogger.step_info(f"初始问题: {initial_state['problem']}")
    VisualLogger.step_info(f"待分析异常指标: {', '.join(initial_state['reasons'])}")
    workflow = create_workflow()
    VisualLogger.step_info("工作流创建完成，开始执行...")
    final_state = workflow.invoke(initial_state)
    visualize_final_result(final_state)
    VisualLogger.step_success("工作流执行完成！")