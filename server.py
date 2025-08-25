
import json
from flask import *
from flask_cors import CORS
from core_utils.split_body import *
from core_utils.send_email import *
from my_ollama.ask_ollama import *
from services.analysis import *
from services.prediction import *
from get_data.api_connectors import *
from workflow.process import *
from waitress import serve
from core_utils.printt import *
app = Flask(__name__)
CORS(app)


@app.route('/fenxi', methods=['POST'])
def Output():
    input_data = request.get_json()
    data,mod = split_body(input_data)
    string_data = json.dumps(data, ensure_ascii=False)
    prompt = ""
    system_prompt=""
    if mod==4:
        prompt,system_prompt=production_analysis(string_data)
    elif mod==5:
        prompt,system_prompt=Car_evaluation_analysis(string_data)
    elif mod==6:
        prompt,system_prompt=Production_Problems_analysis(string_data)
    elif mod==7:
        data = get_ads_ai_production()
        prompt,system_prompt=production_prediction(data)
    elif mod==8:
        data =get_ads_ai_sales()
        prompt,system_prompt=sales_prediction(data)
    elif mod==9:
        return analyze_problem(
        "production_efficiency",
        ["inventory_turnover_rate", "work_hours", "defect_rate"]
        )
    return Response(
        ask_ollama(prompt,system_prompt),
        mimetype="application/x-ndjson"
    )

@app.route('/health')
def hello():
    print("It is health")
    return "It is OK!!"

@app.route("/email",methods=["POST"])
def send_email():
    input_data = request.get_json()
    subject=input_data['subject']
    content=input_data['content']
    send_qq_email(subject,content,is_html=False) # type: ignore
    return {"code":200,"msg":"发送成功"}

if __name__ == '__main__':
    Run_server()
    serve(app, host='0.0.0.0', port=5001, threads=6)