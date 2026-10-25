# -*- coding: utf-8 -*-
"""思维生长站 V9.1：公开演示，只提供虚构数据，不储存任何用户上传的图片。"""
import json, os, random
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parent
rng=random.Random(20261025)
GROUPS={
 "策略型思维":["抽象性","多样性","择优性","迁移性"],
 "批判型思维":["质疑性","解构性","辩证性","建构性"],
 "创新型思维":["拓展性","发散性","创造性"]
}
DIMS=[v for vs in GROUPS.values() for v in vs]
GRADE={i:f"{'一二三四五六'[i-1]}年级" for i in range(1,7)}
SRC=[
("数与代数","用小棒表示10和1，怎样看出十进制？"),("图形与几何","哪些图形放大后还是同一种图形？"),("统计与概率","最喜欢的课间活动怎样调查更公平？"),("综合与实践","为班级图书角分类设计标签"),("数与代数","9+6为什么可以想成10+5？"),
("数与代数","同一个乘法算式能解决哪些问题？"),("图形与几何","怎样比较两个图形的周长？"),("统计与概率","记录一周天气，怎样整理更清楚？"),("综合与实践","设计值日表怎样更合理？"),("数与代数","平均分后有余数说明了什么？"),
("数与代数","分数的大小只看分母吗？"),("图形与几何","面积和周长有什么不同？"),("统计与概率","评选吉祥物：怎样让结论可信？"),("综合与实践","为秋游准备购物清单与预算"),("数与代数","为什么13÷4的余数1还能继续分？"),
("数与代数","运算律能帮我们发现什么？"),("图形与几何","平移、旋转后哪些属性不变？"),("统计与概率","平均数会掩盖什么信息？"),("综合与实践","设计班级节水方案"),("数与代数","用字母表示数有什么好处？"),
("数与代数","分数乘法为什么这样算？"),("图形与几何","怎样推导平行四边形面积？"),("统计与概率","根据统计图能得出哪些结论？"),("综合与实践","比较两条研学路线的优劣"),("数与代数","方程两边为什么要同时变化？"),
("数与代数","比例关系怎样帮助解决问题？"),("图形与几何","圆面积公式从哪里来？"),("统计与概率","抽样调查怎样才更可靠？"),("综合与实践","为毕业活动做方案优化"),("数与代数","不同算法为什么本质相通？")]
TASKS=[]
for i,(domain,title) in enumerate(SRC):
 g=i//5+1
 TASKS.append({"id":i+1,"grade":g,"grade_text":GRADE[g],"domain":domain,"title":title,"phase":["课前","课堂","课后"][i%3],"concept":{"数与代数":"数量关系与算理","图形与几何":"图形关系与空间观念","统计与概率":"数据证据与理性判断","综合与实践":"真实问题与数学建模"}[domain],"prompt":f"围绕“{title}”进行探究：提出猜想，用算式、图示或表格说明理由；比较两种不同策略，再尝试迁移到新的情境。"})
NAMES=["星星","晨曦","明月","云朵","小树","乐乐","可可","山川","远航","小禾","清川","果果","小雨","小林","知知","悦悦","天天","安安"]
STUDENTS=[{"id":i+1,"alias":"演示·"+name,"grade":i%6+1,"grade_text":GRADE[i%6+1],"class_name":GRADE[i%6+1]+"（1）班"} for i,name in enumerate(NAMES)]
ANSWERS=[
"我先用图示表达关系，再用算式验证。比较后发现原来的方法更直观，但条件变化时需要调整。",
"我先提出猜想，然后通过列举例子与反例来检验，最后把复杂问题转化成学过的基本问题。",
"我尝试了两种方案，一种计算快，另一种更容易解释理由，比较之后选择有证据支持的方法。",
"我先整理已知条件，寻找与旧知识的联系。通过变式比较发现结论成立还需要额外条件。"]
FEEDBACK=[
"能够比较不同方法并说明部分依据，建议补充反例检验与概括。",
"能从已有经验出发化归，下一步尝试提炼一般规律。",
"表现出迁移意识，建议增加数据、图示或数量关系方面的证据。",
"能对已有方法提出质疑，下一步可增强多角度论证。"]
SUBMISSIONS=[];EVALUATIONS=[]
for i in range(300):
 s=STUDENTS[i%len(STUDENTS)]
 task=rng.choice([t for t in TASKS if t["grade"]==s["grade"]])
 base=2.35 + (s["id"]%6-2)*.12+(i%12-6)*.02
 scores={d:max(1,min(4,round(rng.gauss(base,.66)))) for d in DIMS}
 primary={g:round(sum(scores[d] for d in ds)/len(ds),2) for g,ds in GROUPS.items()}
 mean=sum(primary.values())/len(GROUPS)
 lev="基础" if mean<2.2 else "发展" if mean<3.1 else "提升"
 sid=i+1
 SUBMISSIONS.append({"id":sid,"student_id":s["id"],"task_id":task["id"],"task_title":task["title"],"domain":task["domain"],"grade":s["grade"],"answer":rng.choice(ANSWERS),"created":f"2026-10-{i%25+1:02d}","demo":True})
 EVALUATIONS.append({"id":sid,"submission_id":sid,"student_id":s["id"],"task_id":task["id"],"primary":primary,"ratings":scores,"overall_level":lev,"feedback":rng.choice(FEEDBACK),"demo":True})
CHATS=[{"id":i+1,"student_id":STUDENTS[i%18]["id"],"task_id":TASKS[i%30]["id"],"mode":["启发式","建构式","评估式"][i%3],"question":["为什么这个方法也可以？","如果条件变了怎么办？","怎样证明结论？"][i%3],"reply":"先说出依据，再比较不同方法，试着寻找反例。"} for i in range(120)]
UPLOADS=[{"id":i+1,"student_id":STUDENTS[i%18]["id"],"task_id":TASKS[i%30]["id"],"image_name":f"demo_work_{i+1:03d}.jpg","type":["手写演算","几何作图","统计图表","思维导图"][i%4],"analysis":"虚构作品示例：可以补充关键步骤、表达数学依据并比较策略。"} for i in range(36)]
DASHBOARD={
 "primary_groups":GROUPS,
 "primary_summary":{g:round(sum(e["primary"][g] for e in EVALUATIONS)/len(EVALUATIONS),2) for g in GROUPS},
 "secondary_avg":[{"name":d,"value":round(sum(e["ratings"][d] for e in EVALUATIONS)/len(EVALUATIONS),2)} for d in DIMS],
 "trend":[{"period":f"分组{i+1}","avg":round(sum(sum(e["primary"].values())/len(GROUPS) for e in EVALUATIONS[i*30:(i+1)*30])/30,2)} for i in range(10)],
 "domain_distribution":[{"name":d,"value":sum(s["domain"]==d for s in SUBMISSIONS)} for d in ("数与代数","图形与几何","统计与概率","综合与实践")],
 "level_distribution":[{"name":lev,"value":sum(e["overall_level"]==lev for e in EVALUATIONS)} for lev in ("基础","发展","提升")]
}
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def send(self,obj,status=200,content_type="application/json; charset=utf-8"):
  data=obj if isinstance(obj,bytes) else json.dumps(obj,ensure_ascii=False).encode("utf-8")
  self.send_response(status)
  for k,v in {"Content-Type":content_type,"Content-Length":str(len(data)),"Cache-Control":"no-store","X-Content-Type-Options":"nosniff","Referrer-Policy":"no-referrer","X-Frame-Options":"SAMEORIGIN"}.items():self.send_header(k,v)
  self.end_headers();self.wfile.write(data)
 def do_GET(self):
  path=urlsplit(self.path).path
  if path in ("/","/index.html","/teacher.html","/student.html"):
   return self.send((ROOT/"index.html").read_bytes(),content_type="text/html; charset=utf-8")
  routes={"/api/tasks":TASKS,"/api/students":STUDENTS,"/api/submissions":SUBMISSIONS,"/api/evaluations":EVALUATIONS,"/api/chats":CHATS,"/api/uploads":UPLOADS,"/api/dashboard":DASHBOARD,"/api/status":{"ok":True,"version":"V10稳定图表三维评价体验","demo_only":True,"task_count":len(TASKS),"submission_count":len(SUBMISSIONS),"evaluation_count":len(EVALUATIONS),"secondary_count":len(DIMS),"image_upload":"browser-local-preview-no-storage"}}
  if path in routes:return self.send(routes[path])
  return self.send({"error":"not found"},404)
 def do_POST(self):
  length=int(self.headers.get("Content-Length","0"))
  if length>8192 or length<0:return self.send({"error":"不支持文件传输；请只提交简短的数学问题。"},413)
  try:data=json.loads(self.rfile.read(length)) if length else {}
  except Exception:return self.send({"error":"无效请求"},400)
  if not isinstance(data,dict):return self.send({"error":"无效请求"},400)
  if urlsplit(self.path).path!="/api/chat":return self.send({"error":"公网演示不接收实际学生数据或图片，所有作答与评价仅为虚构样例。"},403)
  q=str(data.get("question",""))[:300].strip(); mode=data.get("mode","启发式")
  if not q:return self.send({"error":"请输入问题"},400)
  reply={"启发式":"先说说你知道什么，以及已经尝试了哪些方法。能不能找一个反例？","建构式":"你能用图示、表格或数量关系式表达题目，再比较两种解题思路吗？","评估式":"你的结论有哪些依据？如果改变一个条件还成立吗？你会如何验证？"}.get(mode,"先描述你的猜想和依据。")
  return self.send({"reply":reply,"saved":False,"demo_only":True})
if __name__=="__main__":
 port=int(os.getenv("PORT","10000"));print(f"思维生长站V9.1免费演示端口{port}",flush=True);ThreadingHTTPServer(("0.0.0.0",port),Handler).serve_forever()