
const $=s=>document.querySelector(s), esc=s=>String(s).replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]));
function clock(){ $("#clock").textContent=new Date().toLocaleTimeString(); } setInterval(clock,1000);clock();

async function run(q){if(!q.trim())return;$("#resp").textContent="Processing...";let d=await(await fetch("/api/command",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({command:q})})).json();let r=d.response;
if(r.startsWith("OPEN:")){window.open(r.slice(5),"_blank");$("#resp").textContent="Opening website..."}else if(r.startsWith("SEARCH:")){window.open("https://www.google.com/search?q="+r.slice(7),"_blank");$("#resp").textContent="Opening search..."}else $("#resp").textContent=r;refreshStats();}
$("#run").onclick=()=>run($("#cmd").value);$("#cmd").onkeydown=e=>{if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();run($("#cmd").value)}};
document.querySelectorAll(".quick button").forEach(x=>x.onclick=()=>run(x.dataset.c));
document.querySelectorAll(".nav").forEach(x=>x.onclick=()=>{document.querySelectorAll(".nav").forEach(n=>n.classList.remove("active"));x.classList.add("active");document.querySelectorAll(".panel").forEach(p=>p.classList.remove("active"));$("#"+x.dataset.p).classList.add("active");if(x.dataset.p==="history")loadHistory();if(x.dataset.p==="notes")loadNotes();if(x.dataset.p==="reminders")loadReminders()});

async function loadHistory(){let d=await(await fetch("/api/history")).json();$("#historyList").innerHTML=d.length?d.map(x=>`<article><time>${x.created_at}</time><b>${esc(x.command)}</b><p>${esc(x.response)}</p></article>`).join(""):"<p>No history yet.</p>";}
async function loadNotes(){let d=await(await fetch("/api/notes")).json();$("#notesList").innerHTML=d.length?d.map(x=>`<article><button onclick="delNote(${x.id})">Delete</button><b>${esc(x.title)}</b><p>${esc(x.body)}</p><small>${x.created_at}</small></article>`).join(""):"<p>No notes yet.</p>";}
$("#saveNote").onclick=async()=>{let title=$("#nt").value.trim(),body=$("#nb").value.trim();if(!title||!body)return;await fetch("/api/notes",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({title,body})});$("#nt").value="";$("#nb").value="";loadNotes();refreshStats()};
async function delNote(i){await fetch("/api/notes/"+i,{method:"DELETE"});loadNotes();refreshStats()}
async function loadReminders(){let d=await(await fetch("/api/reminders")).json();$("#remList").innerHTML=d.length?d.map(x=>`<article><button onclick="delRem(${x.id})">Delete</button><b>${esc(x.title)}</b><p>⏰ ${esc(x.remind_at)}</p></article>`).join(""):"<p>No reminders yet.</p>";}
$("#saveReminder").onclick=async()=>{let title=$("#rt").value.trim(),at=$("#ra").value;if(!title||!at)return;await fetch("/api/reminders",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({title,remind_at:at})});$("#rt").value="";$("#ra").value="";loadReminders();refreshStats();};
async function delRem(i){await fetch("/api/reminders/"+i,{method:"DELETE"});loadReminders();refreshStats()}
async function refreshStats(){let [h,n,r]=await Promise.all([fetch("/api/history").then(x=>x.json()),fetch("/api/notes").then(x=>x.json()),fetch("/api/reminders").then(x=>x.json())]);$("#historyCount").textContent=h.length;$("#noteCount").textContent=n.length;$("#remCount").textContent=r.length}
if("SpeechRecognition"in window||"webkitSpeechRecognition"in window){let S=window.SpeechRecognition||window.webkitSpeechRecognition,rec=new S();rec.lang="en-US";rec.onresult=e=>{let q=e.results[0][0].transcript;$("#cmd").value=q;run(q)};$("#mic").onclick=()=>rec.start()}else $("#mic").onclick=()=>alert("Speech recognition is not supported here.");
if("serviceWorker"in navigator) navigator.serviceWorker.register("/static/sw.js").catch(()=>{});
refreshStats();
