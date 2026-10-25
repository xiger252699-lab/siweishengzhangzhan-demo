
/* V11 shared RAM-only demo workflow */
let W=null, selectedAnswerId=null;
const wtask=id=>[...(R.tasks||[]),...((W&&W.tasks)||[])].find(t=>t.id===Number(id));
const wtall=()=>[...(R.tasks||[]),...((W&&W.tasks)||[])];
const warn='<div style="border:1px solid #705d36;background:#30291f;color:#ffe2ab;padding:12px;border-radius:10px;margin:12px 0;font-size:13px">仅供虚构学生演示，不得填写真实个人信息。教师布置、学生作答和点评只存于内存，Render 重启即恢复预置状态。</div>';
const pane=(title,html)=>'<article class="panel"><h2>'+title+'</h2>'+html+'</article>';
const field=(label,el)=>'<label style="display:block;margin:12px 0;color:#cad9ed;font-size:13px">'+label+el+'</label>';
const control='style="width:100%;background:#0e1c34;color:#f6fbff;border:1px solid #365478;border-radius:9px;padding:10px;margin-top:7px"';
const wfMsg=(s)=>{const el=$('wfMessage')||$('wsMessage');if(el)el.textContent=s;};
async function wfReq(name,obj,isTeacher=false){
 const h={'Content-Type':'application/json'};if(isTeacher)h['X-Demo-Teacher']=sessionStorage.getItem('swTeacherDemoCode')||'';
 const res=await fetch('/api/demo/'+name,{method:'POST',headers:h,body:JSON.stringify(obj)});
 const data=await res.json();if(!res.ok)throw Error(data.error||'操作失败');return data;
}
async function wfRefresh(){try{const r=await fetch('/api/demo/state',{cache:'no-store'});if(!r.ok)throw Error('接口异常');W=await r.json();if(view==='teacher'){fillAssign();fillReview();}if(view==='student')fillStudent();}catch(e){wfMsg('无法读取互动数据：'+e.message);}}
function teacherWF(){
 const part='<div class="section-head"><h2>任务布置与教师点评</h2><span>恢复教师操作链</span></div>'+warn+
 '<div class="panel" style="margin-bottom:16px"><h2>教师体验授权</h2><div class="controlbar"><input id="wfCode" type="password" placeholder="教师体验口令" '+control+'><button class="btn" onclick="wfLogin()">验证</button></div><p class="desc">只有持有体验口令的教师能发布任务与评价；当前为公开虚构数据环境。</p></div>'+
 '<div class="profile-grid">'+pane('① 布置新任务',field('题目名称','<input '+control+' id="wfTitle" maxlength="90" placeholder="写出数学探究主题">')+field('年级','<select '+control+' id="wfGrade">'+[1,2,3,4,5,6].map(x=>'<option value="'+x+'">'+x+'年级</option>').join('')+'</select>')+field('学习领域','<select '+control+' id="wfDomain">'+['数与代数','图形与几何','统计与概率','综合与实践'].map(x=>'<option>'+x+'</option>').join('')+'</select>')+field('任务说明','<textarea '+control+' id="wfPrompt" maxlength="900" rows="4" placeholder="15字以上：情境、问题、探究要求"></textarea>')+'<button class="btn" onclick="wfCreate()">创建任务</button>')+
 pane('② 分配给演示学生',field('选择已有任务','<select '+control+' id="wfAssignTask"></select>')+field('接收任务的学生','<div id="wfStudents" style="display:grid;grid-template-columns:repeat(2,1fr);gap:8px;margin-top:8px"></div>')+field('教师提醒','<input '+control+' id="wfAssignNote" maxlength="240" placeholder="先独立探究……">')+'<button class="btn" onclick="wfAssign()">布置给所选学生</button>')+'</div>'+
 '<div class="profile-grid" style="margin-top:16px">'+pane('③ 查看学生作答与版本','<div id="wfResponses" style="max-height:430px;overflow:auto"></div>')+
 pane('④ 教师点评与11项评价','<div id="wfChosen" class="muted" style="margin:10px 0">请先点击左侧一份作答。</div>'+field('教师反馈','<textarea '+control+' id="wfComment" maxlength="900" rows="3" placeholder="依据、优势、建议"></textarea>')+'<div id="wfDims" style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px">'+dimensions.map(x=>'<label style="font-size:12px;color:#cde0f4">'+safe(x)+'<select '+control+' data-wfd="'+safe(x)+'"><option value="">未观察</option>'+[1,2,3,4].map(i=>'<option value="'+i+'">'+i+'级</option>').join('')+'</select></label>').join('')+'</div><button class="btn" style="margin-top:15px" onclick="wfReview()">发布点评</button>')+'</div>'+
 pane('已布置的演示任务','<div id="wfAssignments"></div>')+'<div id="wfMessage" class="wf-msg" style="padding:12px;color:#9adbc9"></div>';
 let a=document.querySelector('main.wrap .section-head');if(a)a.insertAdjacentHTML('beforebegin',part);
 wfRefresh();
}
async function wfLogin(){sessionStorage.setItem('swTeacherDemoCode',$('wfCode').value.trim());try{await wfReq('verify',{},true);wfMsg('教师体验口令验证成功');}catch(e){sessionStorage.removeItem('swTeacherDemoCode');wfMsg(e.message);}}
async function wfCreate(){try{await wfReq('create-task',{title:$('wfTitle').value,grade:Number($('wfGrade').value),domain:$('wfDomain').value,prompt:$('wfPrompt').value},true);wfMsg('已创建任务');$('wfTitle').value='';$('wfPrompt').value='';await wfRefresh();}catch(e){wfMsg(e.message);}}
async function wfAssign(){const ids=[...document.querySelectorAll('#wfStudents input:checked')].map(x=>Number(x.value));try{await wfReq('assign',{task_id:Number($('wfAssignTask').value),student_ids:ids,note:$('wfAssignNote').value},true);wfMsg('已布置任务给'+ids.length+'位演示学生');await wfRefresh();}catch(e){wfMsg(e.message);}}
function fillAssign(){
 const select=$('wfAssignTask');if(!select)return;const old=select.value;select.innerHTML=wtall().map(t=>'<option value="'+t.id+'">'+safe(t.grade_text)+' · '+safe(t.title)+'</option>').join('');if(old)select.value=old;
 const checks=$('wfStudents');const chosen=new Set([...checks.querySelectorAll('input:checked')].map(x=>x.value));
 checks.innerHTML=students().map(s=>'<label style="font-size:13px"><input type="checkbox" value="'+s.id+'" '+(chosen.has(String(s.id))?'checked':'')+'> '+safe(s.alias)+'</label>').join('');
 $('wfAssignments').innerHTML=W.assignments.slice().reverse().slice(0,12).map(a=>'<div class="wf-record" style="padding:10px;border-bottom:1px solid #2e4665">'+safe(wtask(a.task_id)?.title)+'　<span class="muted">'+a.student_ids.length+'人 · '+safe(a.created)+'</span></div>').join('');
}
function fillReview(){
 $('wfResponses').innerHTML=W.submissions.slice().reverse().map(s=>{let st=students().find(x=>x.id===s.student_id);return '<div style="padding:13px;border:1px solid #2b4469;border-radius:12px;margin:9px 0"><strong>'+safe(st?.alias)+' · '+safe(wtask(s.task_id)?.title)+'</strong><p style="font-size:13px;line-height:1.6">'+safe(s.answer)+'</p><small class="muted">第'+s.version+'版</small><div><button class="btn soft" onclick="wfPickReview('+s.id+')">点评／查看版本</button></div></div>';}).join('');
}
function wfPickReview(id){
 const s=W.submissions.find(x=>x.id===id);if(!s)return;selectedAnswerId=id;
 const rev=W.reviews.find(x=>x.submission_id===id);
 $('wfChosen').innerHTML='<strong>'+safe(wtask(s.task_id)?.title)+'</strong><p>'+safe(s.answer)+'</p><details><summary>查看'+s.history.length+'个版本</summary>'+s.history.map(v=>'<div style="padding:10px;border-bottom:1px solid #364762">第'+v.version+'版：'+safe(v.answer)+'</div>').join('')+'</details>';
 $('wfComment').value=rev?.comment||'';
 document.querySelectorAll('#wfDims select').forEach(x=>x.value=rev?.ratings?.[x.dataset.wfd]||'');
}
async function wfReview(){if(!selectedAnswerId)return wfMsg('请先选择一份作答');const ratings={};document.querySelectorAll('#wfDims select').forEach(x=>{if(x.value)ratings[x.dataset.wfd]=Number(x.value);});try{await wfReq('review',{submission_id:selectedAnswerId,comment:$('wfComment').value,ratings},true);wfMsg('教师点评已发布；学生可在自己的任务中看到');await wfRefresh();}catch(e){wfMsg(e.message);}}
function studentWF(){
 const sel=students().map(s=>'<option value="'+s.id+'">'+safe(s.alias)+' · '+safe(s.grade_text)+'</option>').join('');
 const p='<div class="section-head"><h2>我的数学探究任务</h2><span>选题 · 作答 · 修订 · 查收教师点评</span></div>'+warn+
 '<section class="profile-grid">'+pane('① 选择任务并记录思考',field('虚构演示学生','<select '+control+' id="wsStudent" onchange="wsChanged()">'+sel+'</select>')+field('选择数学任务','<select '+control+' id="wsTask" onchange="wsChanged()"></select>')+'<div class="wf-msg" id="wsTaskInfo" style="padding:11px;line-height:1.7"></div>'+field('我的探究思路','<textarea '+control+' id="wsAnswer" rows="5" maxlength="2000" placeholder="先提出猜想，再解释、比较和检验……"></textarea>')+'<button class="btn" onclick="wsSubmit()">提交／修改作答</button><div class="wf-msg" id="wsMessage" style="padding:9px"></div>')+
 pane('② 查收教师反馈','<div id="wsFeedback">选择任务后显示反馈。</div>')+'</section>'+
 pane('老师布置给我的任务','<div id="wsAssignments"></div>');
 const anchor=document.getElementById('taskArea');if(anchor)anchor.insertAdjacentHTML('beforebegin',p);
 const old=updateTasks;updateTasks=function(){old();const gr=$('gradeFilter')?.value||'',domain=$('domainFilter')?.value||'',ts=R.tasks.filter(t=>(!gr||t.grade==gr)&&(!domain||t.domain===domain));[...$('taskGrid').children].forEach((el,i)=>{if(ts[i]){const b=document.createElement('button');b.className='btn soft';b.textContent='选择此题';b.onclick=()=>wsPick(ts[i].id);el.appendChild(b);}});};updateTasks();wfRefresh();
}
function wsPick(t){$('wsTask').value=String(t);wsChanged();$('wsTaskInfo').scrollIntoView({block:'center',behavior:'smooth'});}
function wsChanged(){if(!W)return;const t=wtask($('wsTask').value),s=Number($('wsStudent').value);$('wsTaskInfo').innerHTML=t?'<b>'+safe(t.title)+'</b><p>'+safe(t.prompt)+'</p>':'请选择数学任务';
 const sub=W.submissions.find(x=>x.student_id===s&&x.task_id===Number($('wsTask').value)),review=sub?W.reviews.find(x=>x.submission_id===sub.id):null;
 $('wsFeedback').innerHTML=sub?'<h3>我的第'+sub.version+'版作答</h3><p>'+safe(sub.answer)+'</p><details><summary>历史修改版本</summary>'+sub.history.map(h=>'<p>第'+h.version+'版：'+safe(h.answer)+'</p>').join('')+'</details>'+(review?'<div class="wf-msg"><strong>老师点评</strong><p>'+safe(review.comment)+'</p><p>'+Object.entries(review.ratings).map(([k,v])=>safe(k)+v+'级').join('、')+'</p>'+(review.version<sub.version?'<small>点评针对上一版本</small>':'')+'</div>':'<p class="muted">老师尚未点评</p>'):'当前任务尚未提交。';
 $('wsAssignments').innerHTML=W.assignments.filter(a=>a.student_ids.includes(s)).slice().reverse().map(a=>'<div style="padding:13px;border-bottom:1px solid #334761"><strong>'+safe(wtask(a.task_id)?.title)+'</strong><p class="muted">'+safe(a.note||'请先独立思考')+'</p><button class="btn soft" onclick="wsPick('+a.task_id+')">选择任务</button></div>').join('')||'<p class="muted">暂无布置的任务，可自由选择任务。</p>';
}
function fillStudent(){const el=$('wsTask');if(!el)return;const old=el.value;el.innerHTML=wtall().map(t=>'<option value="'+t.id+'">'+safe(t.grade_text)+' · '+safe(t.title)+'</option>').join('');if(old)el.value=old;wsChanged();}
async function wsSubmit(){try{const out=await wfReq('submit',{student_id:Number($('wsStudent').value),task_id:Number($('wsTask').value),answer:$('wsAnswer').value});$('wsMessage').textContent=out.action==='revised'?'修订已保存':'作答已提交';$('wsAnswer').value='';await wfRefresh();}catch(e){$('wsMessage').textContent=e.message;}}
const oldTeacher=teacher,oldStudent=student;
teacher=function(){oldTeacher();teacherWF();};
student=function(){oldStudent();studentWF();};
