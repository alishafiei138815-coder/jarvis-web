
from flask import Flask, render_template, request, jsonify
from datetime import datetime
from pathlib import Path
import sqlite3, re, math, urllib.parse

BASE = Path(__file__).resolve().parent
DB = BASE / "jarvis.db"
app = Flask(__name__)

def conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init():
    c=conn()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS commands(
      id INTEGER PRIMARY KEY AUTOINCREMENT, command TEXT, response TEXT, created_at TEXT);
    CREATE TABLE IF NOT EXISTS notes(
      id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, body TEXT, created_at TEXT);
    CREATE TABLE IF NOT EXISTS reminders(
      id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, remind_at TEXT, done INTEGER DEFAULT 0);
    """)
    c.commit(); c.close()

def log(command,response):
    c=conn()
    c.execute("INSERT INTO commands(command,response,created_at) VALUES(?,?,?)",
              (command,response,datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    c.commit(); c.close()

def calc(expr):
    expr=expr.replace("^","**").strip()
    if not re.fullmatch(r"[0-9+\-*/().% *]+",expr):
        raise ValueError
    return eval(expr,{"__builtins__":{}},{})

def engine(command):
    q=command.strip()
    l=q.lower()
    if not q: return "Give me a command."
    if l in {"hi","hello","hey","سلام","سلام جرویس"}:
        return "Hello. Jarvis Web is online."
    if "time" in l or "ساعت" in l:
        return datetime.now().strftime("Local time: %H:%M:%S")
    if "date" in l or "تاریخ" in l:
        return datetime.now().strftime("Date: %Y-%m-%d")
    if l.startswith(("calculate ","calc ","محاسبه ")):
        expr=re.sub(r"^(calculate|calc|محاسبه)\s*","",q,flags=re.I)
        try: return f"Result: {calc(expr)}"
        except: return "I couldn't calculate that. Example: calculate 18 * 7"
    if l.startswith(("search ","جستجو ")):
        term=re.sub(r"^(search|جستجو)\s*","",q,flags=re.I).strip()
        if not term:return "What should I search for?"
        return "SEARCH:"+urllib.parse.quote_plus(term)
    if l.startswith(("open ","باز کن ")):
        target=re.sub(r"^(open|باز کن)\s*","",q,flags=re.I).lower().strip()
        sites={"youtube":"https://youtube.com","google":"https://google.com","github":"https://github.com"}
        return "OPEN:"+sites[target] if target in sites else "Supported sites: Google, YouTube, GitHub."
    if "help" in l or "کمک" in l:
        return "Try time, date, calculate 12*8, search Python, open youtube, or use Notes and Reminders."
    return "That skill is not installed yet. The V2 architecture is ready for more skills."

@app.route("/")
def home(): return render_template("index.html")

@app.post("/api/command")
def command():
    q=str((request.get_json() or {}).get("command",""))
    r=engine(q)
    log(q,r)
    return jsonify(ok=True,response=r)

@app.get("/api/history")
def history():
    c=conn(); rows=c.execute("SELECT * FROM commands ORDER BY id DESC LIMIT 100").fetchall(); c.close()
    return jsonify([dict(x) for x in rows])

@app.get("/api/notes")
def notes():
    c=conn(); rows=c.execute("SELECT * FROM notes ORDER BY id DESC").fetchall(); c.close()
    return jsonify([dict(x) for x in rows])

@app.post("/api/notes")
def add_note():
    d=request.get_json() or {}; title=str(d.get("title","")).strip(); body=str(d.get("body","")).strip()
    if not title or not body:return jsonify(ok=False,error="Title and body are required"),400
    c=conn(); c.execute("INSERT INTO notes(title,body,created_at) VALUES(?,?,?)",
        (title,body,datetime.now().strftime("%Y-%m-%d %H:%M:%S"))); c.commit(); c.close()
    return jsonify(ok=True)

@app.delete("/api/notes/<int:i>")
def del_note(i):
    c=conn(); c.execute("DELETE FROM notes WHERE id=?",(i,)); c.commit(); c.close()
    return jsonify(ok=True)

@app.get("/api/reminders")
def reminders():
    c=conn(); rows=c.execute("SELECT * FROM reminders ORDER BY remind_at").fetchall(); c.close()
    return jsonify([dict(x) for x in rows])

@app.post("/api/reminders")
def add_reminder():
    d=request.get_json() or {}; title=str(d.get("title","")).strip(); at=str(d.get("remind_at","")).strip()
    if not title or not at:return jsonify(ok=False,error="Title and date/time are required"),400
    c=conn(); c.execute("INSERT INTO reminders(title,remind_at) VALUES(?,?)",(title,at)); c.commit(); c.close()
    return jsonify(ok=True)

@app.delete("/api/reminders/<int:i>")
def del_reminder(i):
    c=conn(); c.execute("DELETE FROM reminders WHERE id=?",(i,)); c.commit(); c.close()
    return jsonify(ok=True)

@app.get("/manifest.json")
def manifest():
    return jsonify({
      "name":"JARVIS Web Assistant","short_name":"JARVIS","start_url":"/",
      "display":"standalone","background_color":"#070b12","theme_color":"#070b12",
      "icons":[{"src":"/static/icon.svg","sizes":"any","type":"image/svg+xml","purpose":"any maskable"}]
    })

init()
if __name__=="__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)
