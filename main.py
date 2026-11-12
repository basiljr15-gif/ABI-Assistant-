import os
from typing import List, Dict
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

APP_NAME = "ABI"
OLLAMA_URL = "https://ollama.com/api/chat"
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:31b")

app = FastAPI(title="ABI Assistant")

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(min_length=1, max_length=60)
    model: str | None = None

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML

@app.get("/api/health")
async def health():
    return {"status": "ok", "app": APP_NAME, "ai_provider": "Ollama Cloud"}

@app.get("/api/config")
async def config():
    return {"model": DEFAULT_MODEL}

@app.post("/api/chat")
async def chat(payload: ChatRequest):
    api_key = os.getenv("OLLAMA_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="ABI is not connected yet. Add OLLAMA_API_KEY in your hosting Secrets."
        )

    model = (payload.model or DEFAULT_MODEL).strip()
    if not model or len(model) > 120:
        raise HTTPException(status_code=400, detail="Invalid model name.")

    messages: List[Dict[str, str]] = [
        {
            "role": "system",
            "content": (
                "You are ABI, a capable, honest, warm personal AI assistant. "
                "Be clear and practical. Never claim to have performed an action "
                "unless you actually have. If you are uncertain, say so."
            ),
        }
    ]
    for item in payload.messages:
        if item.role not in ("user", "assistant"):
            raise HTTPException(status_code=400, detail="Unsupported message role.")
        messages.append({"role": item.role, "content": item.content[:12000]})

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=20.0)) as client:
            response = await client.post(
                OLLAMA_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={"model": model, "messages": messages, "stream": False},
            )
        if response.status_code >= 400:
            try:
                detail = response.json().get("error", "Ollama Cloud request failed.")
            except Exception:
                detail = "Ollama Cloud request failed."
            raise HTTPException(status_code=response.status_code, detail=detail)
        data = response.json()
        answer = data.get("message", {}).get("content")
        if not answer:
            raise HTTPException(status_code=502, detail="Ollama returned an empty response.")
        return {"reply": answer, "model": data.get("model", model)}
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Ollama Cloud took too long to respond. Try again.")
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Could not reach Ollama Cloud. Try again shortly.")

HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#090d16">
<title>ABI — First Contact</title>
<style>
:root{color-scheme:dark;--bg:#080c14;--panel:#101827;--panel2:#151f31;--line:#26354a;--text:#edf4ff;--muted:#91a2ba;--cyan:#55d7ed;--blue:#5488ff}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 50% -20%,#18314b 0%,var(--bg) 55%);color:var(--text);font:15px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;min-height:100dvh}
.app{max-width:980px;margin:auto;min-height:100dvh;display:flex;flex-direction:column;padding:0 16px}
header{display:flex;align-items:center;justify-content:space-between;padding:20px 2px;border-bottom:1px solid #26354a}
.brand{display:flex;align-items:center;gap:12px}.orb{width:42px;height:42px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#d9ffff,#55d7ed 22%,#2261a8 58%,#101827 75%);box-shadow:0 0 28px #55d7ed66}
h1{font-size:20px;letter-spacing:.16em;margin:0}.sub{font-size:12px;color:var(--muted)}.status{font-size:12px;color:#8de8c2;border:1px solid #28644e;padding:5px 9px;border-radius:99px}
main{flex:1;display:flex;flex-direction:column;min-height:0}.welcome{text-align:center;padding:42px 12px 20px}.welcome .orb{width:76px;height:76px;margin:0 auto 15px;box-shadow:0 0 45px #55d7ed55}
.welcome h2{font-size:clamp(26px,6vw,38px);margin:4px 0}.welcome p{color:var(--muted);margin:4px auto;max-width:500px}
.chips{display:flex;gap:8px;flex-wrap:wrap;justify-content:center;margin:18px 0}.chip{background:#101b2b;border:1px solid var(--line);border-radius:99px;padding:8px 12px;color:#c9d9ec;font-size:13px;cursor:pointer}
#chat{display:flex;flex-direction:column;gap:14px;padding:10px 0 22px;flex:1}
.msg{max-width:85%;padding:12px 15px;border-radius:17px;white-space:pre-wrap;overflow-wrap:anywhere}.user{align-self:flex-end;background:linear-gradient(135deg,#285ca5,#25447c);border-bottom-right-radius:5px}.assistant{align-self:flex-start;background:var(--panel);border:1px solid var(--line);border-bottom-left-radius:5px}.meta{font-size:11px;color:var(--muted);margin-bottom:4px}
.composer{position:sticky;bottom:0;padding:12px 0 calc(14px + env(safe-area-inset-bottom));background:linear-gradient(transparent,var(--bg) 18%)}
.entry{display:flex;gap:8px;align-items:flex-end;background:#101827;border:1px solid #34445c;border-radius:18px;padding:8px}
textarea{flex:1;resize:none;max-height:150px;min-height:42px;background:transparent;border:0;outline:0;color:var(--text);font:inherit;padding:9px}
button{border:0;cursor:pointer;color:white}.send,.mic{width:42px;height:42px;border-radius:13px;background:linear-gradient(135deg,#268ca9,#3864bd);font-size:18px}.mic{background:#202e42}.mic.active{background:#a13d53}
.tools{display:flex;justify-content:space-between;color:var(--muted);font-size:11px;padding:7px 4px}.tools button{background:none;color:var(--muted);font-size:12px}
#notice{color:#ffbf86;font-size:12px;min-height:18px;padding:4px}
footer{text-align:center;color:#63748d;font-size:11px;padding:4px 0 12px}
@media(min-width:700px){.app{padding:0 28px}.welcome{padding-top:60px}.msg{max-width:75%}}
</style>
</head>
<body><div class="app">
<header><div class="brand"><div class="orb"></div><div><h1>ABI</h1><div class="sub">ARTIFICIAL BRAIN INTELLIGENCE</div></div></div><div class="status" id="status">● Ready</div></header>
<main><section class="welcome" id="welcome"><div class="orb"></div><h2>First Contact</h2><p>Your personal AI assistant, connected to Ollama Cloud.</p>
<div class="chips"><button class="chip" data-prompt="Introduce yourself and explain what you can help me with.">Meet ABI</button><button class="chip" data-prompt="Help me plan my day with practical priorities.">Plan my day</button><button class="chip" data-prompt="Explain how you can help me build a project step by step.">Explore capabilities</button></div></section>
<section id="chat" aria-live="polite"></section></main>
<div class="composer"><div id="notice"></div><div class="entry"><textarea id="input" rows="1" placeholder="Message ABI…"></textarea><button class="mic" id="mic" title="Voice input">🎙</button><button class="send" id="send" title="Send">➤</button></div><div class="tools"><span id="modelLabel">Ollama Cloud · checking…</span><span><button id="speakToggle">🔊 Voice on</button> · <button id="clear">Clear chat</button></span></div></div>
<footer>ABI v0.1 · Your conversations are kept in this browser only in this prototype.</footer>
</div>
<script>
const chatEl=document.getElementById('chat'), input=document.getElementById('input'), notice=document.getElementById('notice');
let messages=JSON.parse(localStorage.getItem('abi_messages')||'[]'), speak=true, busy=false;
function render(){chatEl.innerHTML='';messages.forEach(m=>{const d=document.createElement('div');d.className='msg '+m.role;const who=document.createElement('div');who.className='meta';who.textContent=m.role==='user'?'YOU':'ABI';const body=document.createElement('div');body.textContent=m.content;d.append(who,body);chatEl.append(d)});document.getElementById('welcome').style.display=messages.length?'none':'block';chatEl.scrollTop=chatEl.scrollHeight;window.scrollTo(0,document.body.scrollHeight)}
function save(){localStorage.setItem('abi_messages',JSON.stringify(messages.slice(-60)))}
async function send(text){text=(text||input.value).trim();if(!text||busy)return;input.value='';messages.push({role:'user',content:text});render();save();busy=true;document.getElementById('status').textContent='● Thinking';document.getElementById('send').disabled=true;notice.textContent='';
try{const res=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({messages:messages.slice(-30)})});const data=await res.json();if(!res.ok)throw new Error(data.detail||'Request failed');messages.push({role:'assistant',content:data.reply});document.getElementById('modelLabel').textContent='Ollama Cloud · '+data.model;render();save();if(speak&&'speechSynthesis'in window){speechSynthesis.cancel();speechSynthesis.speak(new SpeechSynthesisUtterance(data.reply))}}
catch(e){notice.textContent='Connection issue: '+e.message;messages.pop();render()}
finally{busy=false;document.getElementById('status').textContent='● Ready';document.getElementById('send').disabled=false}}
document.getElementById('send').onclick=()=>send();input.addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send()}});
document.querySelectorAll('[data-prompt]').forEach(b=>b.onclick=()=>send(b.dataset.prompt));
document.getElementById('clear').onclick=()=>{messages=[];save();render();notice.textContent='This browser chat has been cleared.'};
document.getElementById('speakToggle').onclick=()=>{speak=!speak;document.getElementById('speakToggle').textContent=speak?'🔊 Voice on':'🔇 Voice off'};
const SpeechRecognition=window.SpeechRecognition||window.webkitSpeechRecognition;
const mic=document.getElementById('mic');if(SpeechRecognition){const rec=new SpeechRecognition();rec.lang=navigator.language||'en-US';rec.onresult=e=>{input.value=e.results[0][0].transcript;send()};rec.onerror=()=>{notice.textContent='Voice recognition was unavailable. You can type instead.'};rec.onend=()=>mic.classList.remove('active');mic.onclick=()=>{mic.classList.add('active');rec.start()}}else{mic.disabled=true;mic.title='Voice recognition is not supported in this browser';mic.style.opacity='.45'}
fetch('/api/config').then(r=>r.json()).then(d=>document.getElementById('modelLabel').textContent='Ollama Cloud · '+d.model).catch(()=>{});
render();
</script></body></html>"""
