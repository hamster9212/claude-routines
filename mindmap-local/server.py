"""
MindFlow Local Server
AI: Groq API (완전 무료, 하루 14,400회) — Llama 3.3 70B 사용
"""
import os, json, threading, time, re
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader

try:
    from groq import Groq
    GROQ_OK = True
except ImportError:
    GROQ_OK = False

BASE = os.path.dirname(os.path.abspath(__file__))
MINDMAPS_DIR = os.path.join(BASE, "mindmaps")
UPLOADS_DIR  = os.path.join(BASE, "uploads")
CONFIG_FILE  = os.path.join(BASE, "config.json")
os.makedirs(MINDMAPS_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR,  exist_ok=True)

app = Flask(__name__, static_folder=os.path.join(BASE, "public"))
CORS(app)

# ── 설정 ─────────────────────────────────────────────────────────────────────
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"groq_key": "", "model": "llama-3.3-70b-versatile"}

def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

# ── AI 호출 (Groq) ─────────────────────────────────────────────────────────
def call_ai(prompt: str, timeout: int = 120) -> str:
    cfg = load_config()
    key = cfg.get("groq_key", "").strip()
    if not key:
        raise RuntimeError("Groq API 키가 설정되지 않았습니다. 설정 탭에서 입력하세요.")
    if not GROQ_OK:
        raise RuntimeError("groq 패키지가 설치되지 않았습니다. pip install groq")
    client = Groq(api_key=key)
    resp = client.chat.completions.create(
        model=cfg.get("model", "llama-3.3-70b-versatile"),
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4096,
        temperature=0.3,
    )
    return resp.choices[0].message.content.strip()


# ── PDF 추출 ──────────────────────────────────────────────────────────────────
def extract_pdf(path: str, max_chars=15000):
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += (page.extract_text() or "") + "\n"
        if len(text) >= max_chars:
            break
    return text[:max_chars], len(reader.pages)


# ── 마인드맵 생성 ─────────────────────────────────────────────────────────────
MINDMAP_PROMPT = """다음 PDF 내용을 분석해서 마인드맵을 만들어줘.

학습 목표: {goal}
분석 방향: {focus}

PDF 내용:
{text}

요구사항:
1. markmap 마크다운 형식으로만 출력 (코드블록 없이 순수 마크다운)
2. 최상위 노드: 문서 제목 (# 제목)
3. 2~4 depth 계층
4. 핵심 개념 위주
5. 한국어로 출력

형식:
# 제목
## 대분류 1
### 소분류 1-1
- 세부항목
## 대분류 2
..."""

def bg_generate(sid, pdf_text, name, goal, focus):
    update_meta(sid, status="analyzing")
    try:
        prompt = MINDMAP_PROMPT.format(
            goal=goal or "핵심 개념 파악",
            focus=focus or "전반적인 내용 정리",
            text=pdf_text
        )
        md = call_ai(prompt)
        # 코드블록 제거
        md = re.sub(r"```[^\n]*\n?", "", md).strip()
        write_md(sid, md)
        append_history(sid, "최초 생성", md)
        update_meta(sid, status="done", mindmap=md)
    except Exception as e:
        update_meta(sid, status="error", error=str(e))


# ── 마인드맵 확장 ─────────────────────────────────────────────────────────────
def bg_expand(sid, new_content=None):
    meta = load_meta(sid)
    if not meta or meta.get("status") != "done":
        return
    current = meta.get("mindmap", "")

    if new_content:
        prompt = f"""기존 마인드맵에 오늘 학습한 내용을 자연스럽게 통합해줘.

기존 마인드맵:
{current}

추가할 내용:
{new_content}

요구사항:
- 기존 구조 유지
- 새 내용을 적절한 위치에 추가
- markmap 마크다운 형식 유지 (코드블록 없이)"""
        note = new_content[:60]
    else:
        prompt = f"""다음 마인드맵에 빠진 핵심 개념 3~5개를 추가해줘.

현재 마인드맵:
{current}

요구사항:
- 기존 구조 유지
- 자연스럽게 통합
- markmap 마크다운 형식 유지 (코드블록 없이)"""
        note = "AI 자동 확장"

    try:
        updated = call_ai(prompt)
        updated = re.sub(r"```[^\n]*\n?", "", updated).strip()
        write_md(sid, updated)
        append_history(sid, note, updated)
        update_meta(sid, mindmap=updated)
    except Exception as e:
        print(f"[expand] 오류: {e}")


# ── 4-역할 분석 시스템 ────────────────────────────────────────────────────────
ROLES = {
    "devil": {
        "name": "😈 Devil's Advocate (현실 검증관)",
        "prompt": """당신은 학습 계획의 현실 검증관입니다. 3개월 후 시점에서 역할극을 합니다.

학습 계획:
{plan}

구체적인 실패 시나리오 2~3개를 제시하세요:
- 반드시 날짜/상황/감정 맥락 포함
- "1주차엔 잘 됐는데 3주차에 여자친구랑 싸운 날..." 이런 식으로
- 추상적 비판 금지, 생생한 현실 묘사
- 한국어로"""
    },
    "sustainer": {
        "name": "🌱 Sustainer (지속가능성 설계자)",
        "prompt": """당신은 지속가능성 설계자입니다. 의지력 0을 가정합니다.

문제 시나리오:
{plan}

각 문제에 대한 시스템적 해결책을 제시하세요:
- "더 열심히 하면 됨" 류 절대 금지
- 시스템이 알아서 돌아가도록 설계
- 구체적인 트리거/루틴/환경 설계 위주
- 한국어로"""
    },
    "coach": {
        "name": "🎯 Coach (수렴 중재자)",
        "prompt": """당신은 수렴 중재자입니다.

Devil과 Sustainer의 논쟁:
{plan}

이번 주 월요일부터 실행 가능한 버전으로 압축하세요:
- 최종 산출물: 오늘 할 것 3가지 이하
- 구체적이고 즉시 실행 가능한 것만
- 한국어로"""
    },
    "mirror": {
        "name": "🪞 Mirror (반복 오류 감지기)",
        "prompt": """당신은 반복 오류 감지기입니다.

이 사람의 학습 패턴:
{plan}

반복되는 실패 패턴만 냉정하게 출력하세요:
- 칭찬 완전 금지
- "이 사람은 X하는 패턴이 있음" 형식으로
- 구체적 증거 기반
- 개선 방향도 시스템 관점에서만
- 한국어로"""
    }
}

def bg_analyze(sid, role_key, plan_text):
    meta = load_meta(sid)
    if not meta:
        return
    role = ROLES.get(role_key)
    if not role:
        return
    prompt = role["prompt"].format(plan=plan_text)
    try:
        result = call_ai(prompt)
        analyses = meta.get("analyses", {})
        analyses[role_key] = {"role": role["name"], "result": result, "date": today()}
        update_meta(sid, analyses=analyses)
    except Exception as e:
        meta = load_meta(sid)
        analyses = meta.get("analyses", {})
        analyses[role_key] = {"role": role["name"], "result": f"오류: {e}", "date": today()}
        update_meta(sid, analyses=analyses)


# ── 자동 확장 스케줄러 (매일 오전 9시) ───────────────────────────────────────
def scheduler():
    while True:
        now = datetime.now()
        next_run = now.replace(hour=9, minute=0, second=0, microsecond=0)
        if now >= next_run:
            from datetime import timedelta
            next_run += timedelta(days=1)
        wait = (next_run - now).total_seconds()
        print(f"[스케줄러] 다음 자동 확장: {next_run.strftime('%Y-%m-%d %H:%M')}")
        time.sleep(wait)
        for s in list_sessions():
            if s.get("status") == "done":
                print(f"[스케줄러] 자동 확장: {s['name']}")
                bg_expand(s["id"])
                time.sleep(3)


# ── 메타 유틸 ─────────────────────────────────────────────────────────────────
def today(): return datetime.now().strftime("%Y-%m-%d")

def meta_path(sid): return os.path.join(MINDMAPS_DIR, f"{sid}.json")

def load_meta(sid):
    p = meta_path(sid)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None

def save_meta(sid, meta):
    with open(meta_path(sid), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

def update_meta(sid, **kwargs):
    meta = load_meta(sid) or {}
    meta.update(kwargs)
    save_meta(sid, meta)

def append_history(sid, note, content):
    meta = load_meta(sid) or {}
    meta.setdefault("history", []).append({"date": today(), "note": note, "content": content})
    save_meta(sid, meta)

def write_md(sid, content):
    with open(os.path.join(MINDMAPS_DIR, f"{sid}.md"), "w", encoding="utf-8") as f:
        f.write(content)

def list_sessions():
    result = []
    for f in os.listdir(MINDMAPS_DIR):
        if f.endswith(".json"):
            m = load_meta(f[:-5])
            if m:
                result.append(m)
    return sorted(result, key=lambda x: x.get("created", ""), reverse=True)


# ── API 라우트 ────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(os.path.join(BASE, "public"), "index.html")

@app.route("/api/config", methods=["GET"])
def get_config():
    cfg = load_config()
    cfg["groq_key"] = "***" if cfg.get("groq_key") else ""
    return jsonify(cfg)

@app.route("/api/config", methods=["POST"])
def set_config():
    data = request.get_json()
    cfg = load_config()
    if data.get("groq_key") and data["groq_key"] != "***":
        cfg["groq_key"] = data["groq_key"]
    if data.get("model"):
        cfg["model"] = data["model"]
    save_config(cfg)
    return jsonify({"ok": True})

@app.route("/api/sessions")
def get_sessions():
    return jsonify(list_sessions())

@app.route("/api/sessions/<sid>")
def get_session(sid):
    m = load_meta(sid)
    return jsonify(m) if m else ("Not found", 404)

@app.route("/api/sessions/<sid>", methods=["DELETE"])
def del_session(sid):
    for ext in [".json", ".md"]:
        p = os.path.join(MINDMAPS_DIR, sid + ext)
        if os.path.exists(p): os.remove(p)
    return jsonify({"ok": True})

@app.route("/api/upload", methods=["POST"])
def upload():
    f = request.files.get("file")
    if not f: return jsonify({"error": "파일 없음"}), 400
    sid = str(int(time.time() * 1000))
    pdf_path = os.path.join(UPLOADS_DIR, f"{sid}.pdf")
    f.save(pdf_path)
    try:
        text, pages = extract_pdf(pdf_path)
    except Exception as e:
        return jsonify({"error": f"PDF 읽기 실패: {e}"}), 500

    meta = {
        "id": sid,
        "name": request.form.get("name", f.filename.replace(".pdf","")),
        "goal": request.form.get("goal",""),
        "created": today(), "pages": pages,
        "status": "pending", "mindmap": "",
        "history": [], "analyses": {}, "error": ""
    }
    save_meta(sid, meta)
    threading.Thread(target=bg_generate, args=(
        sid, text,
        meta["name"], meta["goal"],
        request.form.get("focus","")
    ), daemon=True).start()
    return jsonify({"session_id": sid})

@app.route("/api/sessions/<sid>/status")
def get_status(sid):
    m = load_meta(sid)
    if not m: return jsonify({"status": "not_found"}), 404
    return jsonify({"status": m["status"], "mindmap": m.get("mindmap",""), "error": m.get("error","")})

@app.route("/api/sessions/<sid>/expand", methods=["POST"])
def expand(sid):
    data = request.get_json(silent=True) or {}
    threading.Thread(target=bg_expand, args=(sid, data.get("content") or None), daemon=True).start()
    return jsonify({"ok": True})

@app.route("/api/sessions/<sid>/save", methods=["POST"])
def save_mm(sid):
    data = request.get_json()
    md = data.get("mindmap","")
    write_md(sid, md)
    append_history(sid, "수동 편집", md)
    update_meta(sid, mindmap=md)
    return jsonify({"ok": True})

@app.route("/api/sessions/<sid>/analyze", methods=["POST"])
def analyze(sid):
    data = request.get_json()
    role = data.get("role")
    plan = data.get("plan","")
    if role not in ROLES: return jsonify({"error":"unknown role"}), 400
    update_meta(sid, **{f"analyzing_{role}": True})
    threading.Thread(target=bg_analyze, args=(sid, role, plan), daemon=True).start()
    return jsonify({"ok": True})

@app.route("/api/sessions/<sid>/analyses")
def get_analyses(sid):
    m = load_meta(sid)
    return jsonify(m.get("analyses", {})) if m else jsonify({})

@app.route("/api/sessions/standalone/analyze", methods=["POST"])
def analyze_standalone():
    """세션 없이 바로 4-역할 분석 실행 (동기)"""
    data = request.get_json()
    role_key = data.get("role")
    plan = data.get("plan", "")
    if role_key not in ROLES:
        return jsonify({"error": "unknown role"}), 400
    try:
        prompt = ROLES[role_key]["prompt"].format(plan=plan)
        result = call_ai(prompt)
        return jsonify({"role": ROLES[role_key]["name"], "result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    threading.Thread(target=scheduler, daemon=True).start()
    print("=" * 50)
    print("  MindFlow 서버 시작!")
    print("  http://localhost:5050")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5050, debug=False, use_reloader=False)
