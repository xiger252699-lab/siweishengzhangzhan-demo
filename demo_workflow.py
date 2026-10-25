# -*- coding: utf-8 -*-
"""V11 public demo workflow: anonymous fictional students only; RAM-only edits.
Do not use for genuine student records, assessment, uploaded images or PII.
"""
import os
import json
import time
import hmac
import threading
from collections import defaultdict, deque
from datetime import datetime
from urllib.parse import urlsplit

MAX_TASKS = 55
MAX_SUBMISSIONS = 400
MAX_ASSIGNMENTS = 260
DIMS = ("抽象性", "多样性", "择优性", "迁移性", "质疑性", "解构性",
        "辩证性", "建构性", "拓展性", "发散性", "创造性")
DOMAINS = ("数与代数", "图形与几何", "统计与概率", "综合与实践")
LOCK = threading.RLock()
HITS = defaultdict(deque)
created_tasks = []
assignments = [
    {"id": 1, "task_id": 1, "student_ids": [1, 7, 13], "note": "先写自己的猜想，再进行验证。", "created": "演示预置"},
    {"id": 2, "task_id": 13, "student_ids": [3, 9, 15], "note": "关注调查是否公平，并说明数据结论的依据。", "created": "演示预置"},
    {"id": 3, "task_id": 22, "student_ids": [5, 11, 17], "note": "用不同方法进行比较。", "created": "演示预置"},
]
responses = [
    {"id": 10001, "task_id": 1, "student_id": 1,
     "answer": "我先画图表示十个一，再把它捆成一个十。这样发现十和一是不同的计数单位。",
     "version": 1, "history": [{"version": 1, "answer": "我先画图表示十个一，再把它捆成一个十。这样发现十和一是不同的计数单位。", "at": "演示预置"}],
     "updated": "演示预置"},
    {"id": 10002, "task_id": 13, "student_id": 3,
     "answer": "我想先调查全班同学，每人只能投一票，再按同一标准统计。只问好友可能会有偏差。",
     "version": 1, "history": [{"version": 1, "answer": "我想先调查全班同学，每人只能投一票，再按同一标准统计。只问好友可能会有偏差。", "at": "演示预置"}],
     "updated": "演示预置"}
]
reviews = [
    {"submission_id": 10001, "version": 1,
     "comment": "能用实物转化说明计数单位，建议再解释这种方法是否适用于更大的数。",
     "ratings": {"抽象性": 3, "迁移性": 2, "建构性": 3},
     "updated": "演示预置"}
]
NEXT = {"task": 31, "assignment": 4, "response": 10003}

def now():
    return datetime.now().strftime("%m-%d %H:%M")

def fail(msg, status=400):
    return {"ok": False, "error": msg}, status

def attach(Handler, base_tasks, demo_students):
    original_get, original_post = Handler.do_GET, Handler.do_POST
    valid_students = {s["id"] for s in demo_students}
    valid_grades = {s["id"]: s["grade"] for s in demo_students}
    secret = os.getenv("DEMO_TEACHER_CODE", "").strip()
    def full_tasks():
        return base_tasks + created_tasks
    def find_task(tid):
        return next((t for t in full_tasks() if t["id"] == tid), None)
    def teacher_auth(self):
        value = self.headers.get("X-Demo-Teacher", "")
        return bool(secret and value and hmac.compare_digest(value, secret))
    def limited(self, limit=28):
        ip = self.client_address[0]
        key = (ip, "demo")
        with LOCK:
            stamps = HITS[key]
            cutoff = time.monotonic() - 60
            while stamps and stamps[0] < cutoff:
                stamps.popleft()
            if len(stamps) >= limit:
                return True
            stamps.append(time.monotonic())
        return False
    def snapshot():
        # All identities here are purpose-built fictional examples.
        return {
            "ok": True, "demo_only": True, "persistent": False,
            "ephemeral_warning": "所有新任务、提交和点评仅保存在运行内存，免费实例重启后恢复预置演示状态。",
            "tasks": list(created_tasks),
            "assignments": list(assignments),
            "submissions": list(responses),
            "reviews": list(reviews),
            "teacher_code_configured": bool(secret),
            "limits": {"tasks": MAX_TASKS, "submissions": MAX_SUBMISSIONS}
        }
    def get(self):
        path = urlsplit(self.path).path
        if path == "/api/demo/state":
            with LOCK:
                return self.send(snapshot())
        return original_get(self)
    def post(self):
        path = urlsplit(self.path).path
        if not path.startswith("/api/demo/"):
            return original_post(self)
        if self.headers.get("Content-Type", "").split(";")[0].strip().lower() != "application/json":
            return self.send({"error": "请求必须使用JSON格式"}, 415)
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length <= 0 or length > 7500:
            return self.send({"error": "请求内容过大或为空（不接收图片）"}, 413)
        if limited(self):
            return self.send({"error": "操作过于频繁，请稍后再试"}, 429)
        try:
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict): raise ValueError()
        except (ValueError, TypeError):
            return self.send({"error": "无效JSON格式"}, 400)
        teacher_only = path in ("/api/demo/verify", "/api/demo/create-task", "/api/demo/assign", "/api/demo/review")
        if teacher_only and not teacher_auth(self):
            return self.send({"error": "教师体验口令不正确。请在教师工作台填写管理员口令。"}, 403)
        with LOCK:
            try:
                if path == "/api/demo/verify":
                    return self.send({"ok": True, "message": "教师体验口令验证通过"})
                if path == "/api/demo/create-task":
                    if len(created_tasks) >= MAX_TASKS:
                        return self.send({"error": "演示任务达到上限"}, 409)
                    grade = int(data.get("grade", 0))
                    domain = str(data.get("domain", "")).strip()
                    title = str(data.get("title", "")).strip()
                    prompt = str(data.get("prompt", "")).strip()
                    if grade not in range(1, 7) or domain not in DOMAINS or len(title) < 4 or len(title) > 90 or len(prompt) < 15 or len(prompt) > 900:
                        return self.send({"error": "请填写有效的年级、领域、4–90字标题和15–900字任务说明"}, 400)
                    t = {"id": NEXT["task"], "grade": grade, "grade_text": "一二三四五六"[grade-1] + "年级",
                         "domain": domain, "title": title, "prompt": prompt,
                         "phase": "新建任务", "concept": "教师自主设计", "demo": True}
                    NEXT["task"] += 1
                    created_tasks.append(t)
                    return self.send({"ok": True, "task": t})
                if path == "/api/demo/assign":
                    if len(assignments) >= MAX_ASSIGNMENTS:
                        return self.send({"error": "演示布置次数已达上限"}, 409)
                    task_id = int(data.get("task_id", 0))
                    task = find_task(task_id)
                    ids = data.get("student_ids")
                    if not task or not isinstance(ids, list) or len(ids) < 1 or len(ids) > 18:
                        return self.send({"error": "请选择任务和虚构演示学生"}, 400)
                    selected = sorted(set(int(x) for x in ids))
                    if not set(selected).issubset(valid_students):
                        return self.send({"error": "仅允许给虚构演示学生布置任务"}, 400)
                    note = str(data.get("note", "")).strip()[:240]
                    assignment = {"id": NEXT["assignment"], "task_id": task_id,
                                  "student_ids": selected, "note": note, "created": now()}
                    NEXT["assignment"] += 1
                    assignments.append(assignment)
                    return self.send({"ok": True, "assignment": assignment})
                if path == "/api/demo/submit":
                    if len(responses) >= MAX_SUBMISSIONS:
                        return self.send({"error": "演示作答数量已达上限"}, 409)
                    task_id = int(data.get("task_id", 0))
                    student_id = int(data.get("student_id", 0))
                    answer = str(data.get("answer", "")).strip()
                    if not find_task(task_id) or student_id not in valid_students:
                        return self.send({"error": "请选择已有任务和虚构演示学生"}, 400)
                    if len(answer) < 8 or len(answer) > 2000:
                        return self.send({"error": "请填写8–2000字的探究思路"}, 400)
                    old = next((x for x in responses if x["task_id"] == task_id and x["student_id"] == student_id), None)
                    if old:
                        if len(old["history"]) >= 12:
                            return self.send({"error": "该任务的演示修改次数已达上限"}, 409)
                        old["version"] += 1
                        old["answer"] = answer
                        old["updated"] = now()
                        old["history"].append({"version": old["version"], "answer": answer, "at": old["updated"]})
                        return self.send({"ok": True, "submission": old, "action": "revised"})
                    response = {"id": NEXT["response"], "student_id": student_id, "task_id": task_id,
                                "answer": answer, "version": 1, "history": [{"version": 1, "answer": answer, "at": now()}],
                                "updated": now()}
                    NEXT["response"] += 1
                    responses.append(response)
                    return self.send({"ok": True, "submission": response, "action": "created"})
                if path == "/api/demo/review":
                    response_id = int(data.get("submission_id", 0))
                    submission = next((x for x in responses if x["id"] == response_id), None)
                    if not submission:
                        return self.send({"error": "未找到此演示作答"}, 404)
                    comment = str(data.get("comment", "")).strip()
                    raw = data.get("ratings", {})
                    if not isinstance(raw, dict) or len(comment) < 5 or len(comment) > 900:
                        return self.send({"error": "教师点评须为5–900字，并提供合法的维度评分"}, 400)
                    if any(d not in DIMS for d in raw):
                        return self.send({"error": "存在不属于原版框架的评分维度"}, 400)
                    parsed = {}
                    for d, value in raw.items():
                        if value in ("", None, 0):
                            continue
                        if not isinstance(value, int) or isinstance(value, bool) or value not in (1, 2, 3, 4):
                            return self.send({"error": "各维度评分只能是1至4；未观察到的维度请留空"}, 400)
                        parsed[d] = value
                    review = {"submission_id": response_id, "version": submission["version"], "comment": comment,
                              "ratings": parsed, "updated": now()}
                    old = next((x for x in reviews if x["submission_id"] == response_id), None)
                    if old: old.update(review)
                    else: reviews.append(review)
                    return self.send({"ok": True, "review": review})
            except (ValueError, TypeError):
                return self.send({"error": "请求参数格式错误"}, 400)
        return self.send({"error": "接口不存在"}, 404)
    Handler.do_GET = get
    Handler.do_POST = post
