import os
import csv
import openai
from fastapi import FastAPI, Request, HTTPException
from api.models import AssessmentData, AssessmentResponse
from dotenv import load_dotenv
from api.prompts import SYSTEM_PROMPT_TEMPLATE, USER_PROMPT_TEMPLATE
from api.cosmos_retriever import get_answer_text
from collections import defaultdict
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或指定前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = openai.AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version="2024-02-15-preview"
)

# 读取 score_rule.csv，返回 {question_id: [规则1, 规则2, ...]}
def load_score_rules(csv_path):
    rules = {}
    with open(csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)
        for row in reader:
            qid = row[0]
            rules[qid] = row[1:]
    return rules

# 判断是否满足加权规则
def check_weighting(rules, service_offering):
    for rule in rules:
        if not rule:
            continue
        if '-' not in rule:
            continue
        r_name, r_opts = rule.split('-')
        r_name = r_name.strip()
        r_opts = [opt.strip().lower() for opt in r_opts.strip().replace(' ', '').split('or')]
        # 查找serviceOffering中对应的anwserselete
        found = False
        for so in service_offering.values():
            if so.get('question_name') == r_name:
                user_ans = so.get('anwserselete', '').lower()
                if user_ans in r_opts:
                    found = True
                else:
                    return False
        if not found:
            return False
    return True

@app.post("/api/llm-advice")
async def batch_enhance(request: AssessmentData):
    frontend_data = request.dict()  # 直接用 Pydantic 的 dict() 方法
    service_offering = frontend_data['serviceOffering']
    score_rules = load_score_rules('api/score_rule.csv')
    all_questions = []
    # 1. 收集所有问题，按顺序编号
    for section_key, section in frontend_data.items():
        if section_key == "serviceOffering":
            continue
        for q in section.values():
            all_questions.append(q)
    for idx, q in enumerate(all_questions):
        q['question_id'] = f"question_{idx:02d}"
    # 2. 处理加权和新分类
    for q in all_questions:
        qid = q['question_id']
        rules = score_rules.get(qid, [])
        original_score = q.get('score', 0)
        # 规则判断
        add_weight = check_weighting(rules, service_offering)
        if add_weight:
            new_score = original_score * 1.25
        else:
            new_score = original_score
        q['new_score'] = new_score
        # 新分类
        if new_score < -1:
            q['new_category'] = 'Start_Doing'
        elif new_score > 1:
            q['new_category'] = 'Keep_Doing'
        else:
            q['new_category'] = 'Do_More'
    # 3. 检索数据库并增强
    results = []
    for q in all_questions:
        question_id = q['question_id']
        new_category = q['new_category']
        base_text = get_answer_text(question_id, new_category)
        if base_text is None:
            base_text = "未找到数据库答案。"
        # 构建prompt
        prompt = USER_PROMPT_TEMPLATE.format(
            industry=service_offering['industry']['text'],
            original_question=q.get('question', ''),
            retrieved_text=base_text,
            advice_type=new_category,
            query=q.get('question', ''),
            user_answer=q.get('anwser', '')
        )
        # 调用LLM
        try:
            response = client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT_TEMPLATE},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=512
            )
            llm_response = response.choices[0].message.content
        except Exception as e:
            llm_response = f"LLM生成失败: {e}"
        results.append({
            "question_id": question_id,
            "catmapping": q.get('catmapping', ''),
            "category": new_category,
            "enhanced_answer": llm_response,
            "retrieved_base_text": base_text
        })
    # 4. 按catmapping分组输出
    grouped = defaultdict(list)
    for r in results:
        grouped[r['catmapping']].append(r)
    return grouped