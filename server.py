# -*- coding: utf-8 -*-
"""思维生长站：只含虚构样例的公网免费体验应用。严禁用于真实学生数据。"""
import json,os,threading,time,datetime
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlsplit,parse_qs
from pathlib import Path

ROOT=Path(__file__).resolve().parent
LOCK=threading.RLock()
DOMAINS=["数与代数","图形与几何","统计与概率","综合与实践"]
TITLES=[
("数与代数","数的组成：怎样解释十进制？"),("数与代数","分数的大小只看分母吗？"),("数与代数","一个算式有多少种解释？"),("数与代数","为什么要统一计数单位？"),("数与代数","小数和分数有什么联系？"),("数与代数","改变条件后算法还成立吗？"),("数与代数","用字母表示变化的数量"),("数与代数","方程的两边为什么保持相等？"),("数与代数","估算与精算怎样选择？"),("数与代数","运算律能帮助我们发现什么？"),("数与代数","平均分之后如何表示结果？"),("数与代数","同一道题的不同解法"),
("图形与几何","比较图形：什么改变了？"),("图形与几何","周长相等面积一定相等吗？"),("图形与几何","用不同方法推导面积"),("图形与几何","立体展开图的秘密"),("图形与几何","如何验证图形的关系？"),("图形与几何","测量误差来自哪里？"),
("统计与概率","评选吉祥物：怎样让结论可信？"),("统计与概率","数据会说谎吗？"),("统计与概率","怎样设计公平的调查？"),("统计与概率","平均数会掩盖什么？"),("统计与概率","可能性如何比较？"),("统计与概率","根据数据做有依据的决策"),
("综合与实践","两条研学路线如何比较？"),("综合与实践","设计节水方案"),("综合与实践","校园空间怎么规划？"),("综合与实践","怎样优化班级活动预算？"),("综合与实践","设计合理的运动计划"),("综合与实践","从真实问题建立数学模型")]
TASKS=[{"id":i+1,"title":title,"domain":domain,"grade":1+(i%6),"phase":["课前","课堂","课后"][i%3],"prompt":f"围绕“{title}”进行探究：先提出自己的猜想，再使用算式、图示、表格或实例说明理由；比较至少两种思路，并提出一个改变条件后的新问题。","concept":["数量关系","图形关系","数据与证据","问题与模型"][DOMAINS.index(domain)]} for i,(domain,title) in enumerate(TITLES)]
DIMS={"策略型思维":["抽象性","多样性","择优性","迁移性"],"批判型思维":["质疑性","解构性","辩证性","建构性"],"创新型思维":["拓展性","发散性","创造性"]}
STUDENTS=[{"id":i+1,"alias":"演示·"+n,"grade":1+i%6} for i,n in enumerate(["星星","小树","云朵","山川","可可","明月","乐乐","晨曦"])]
SUBMISSIONS=[{"id":i+1,"task_id":(i*7)%30+1,"student_id":i%8+1,"answer":"我先提出一个猜想，然后用图示和算式解释理由。我发现条件改变后要重新判断方法是否合适。","created":"2026-10-20","demo":True} for i in range(70)]
EVALUATIONS=[{"id":x["id"],"submission_id":x["id"],"ratings":{d:(x["id"]+j)%4+1 for j,d in enumerate(sum(DIMS.values(),[]))},"feedback":"演示评语：能够说明部分依据，可以继续比较不同方案并寻找反例。","demo":True} for x in SUBMISSIONS]
CHATS=[]
def reply(q,mode):
 if mode=="建构式":return "小思建议先画图或举例：你能把关键数量与关系标出来吗？这些关系与以前学过的哪些知识相通？"
 if mode=="评估式":return "我们来检验你的结论：依据是什么？是否存在反例？如果改变一个条件，你的结论还成立吗？"
 return "这个问题很有价值！先说说你已经知道什么、尝试过什么。你能提出两种方法并比较它们吗？小思不会代替你思考。"
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def send(self,data,status=200,ctype="application/json; charset=utf-8"):
  body=json.dumps(data,ensure_ascii=False).encode() if not isinstance(data,bytes) else data
  self.send_response(status);self.send_header("Content-Type",ctype);self.send_header("Content-Length",str(len(body)));self.send_header("Cache-Control","no-store");self.send_header("X-Content-Type-Options","nosniff");self.send_header("Referrer-Policy","no-referrer");self.end_headers();self.wfile.write(body)
 def do_GET(self):
  path=urlsplit(self.path).path
  if path in ("/","/index.html","/teacher.html","/student.html"):
   self.send((ROOT/"index.html").read_bytes(),ctype="text/html; charset=utf-8");return
  if path=="/api/status":return self.send({"ok":True,"version":"public-free-demo","demo_only":True,"ephemeral_storage":True,"ai_mode":"规则式数学追问；未连接大模型","task_count":len(TASKS)})
  if path=="/api/tasks":return self.send(TASKS)
  if path=="/api/students":return self.send(STUDENTS)
  if path=="/api/submissions":return self.send(SUBMISSIONS)
  if path=="/api/evaluations":return self.send(EVALUATIONS)
  if path=="/api/chats":return self.send(CHATS[-100:])
  self.send({"error":"not found"},404)
 def do_POST(self):
  path=urlsplit(self.path).path
  length=int(self.headers.get("Content-Length","0"))
  if length<1 or length>4096:return self.send({"error":"请求内容长度不符合要求"},400)
  try:payload=json.loads(self.rfile.read(length))
  except Exception:return self.send({"error":"无效请求"},400)
  if not isinstance(payload,dict):return self.send({"error":"无效请求"},400)
  if path=="/api/chat":
   q=str(payload.get("question",""))[:400].strip();mode=str(payload.get("mode","启发式"))
   if not q:return self.send({"error":"请输入问题"},400)
   if mode not in ["启发式","建构式","评估式"]:mode="启发式"
   return self.send({"reply":reply(q,mode),"mode":mode,"demo_only":True,"saved":False})
  # Public demo disallows actual user-provided submissions or identifiable data.
  return self.send({"error":"本公开体验版只展示虚构数据，不接收真实学生作答或评价。"},403)
if __name__=="__main__":
 port=int(os.getenv("PORT","10000"))
 print(f"思维生长站免费演示站，监听 {port}；不保存真实个人数据",flush=True)
 ThreadingHTTPServer(("0.0.0.0",port),Handler).serve_forever()
