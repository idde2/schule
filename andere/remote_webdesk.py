import io
import time
import threading
from flask import Flask, Response, request, render_template_string
import mss
from PIL import Image
import pyautogui

app = Flask(__name__)
lock = threading.Lock()

html = """
<!doctype html>
<html>
<head>
<title>Web Remote Desktop</title>
<style>
body { margin:0; background:#000; color:#fff; font-family:sans-serif; }
#screen { max-width:100vw; max-height:100vh; cursor:crosshair; }
#top { position:fixed; top:0; left:0; padding:5px; background:#111; z-index:10; }
</style>
</head>
<body>
<div id="top">
Monitor:
<select id="mon">
<option value="1">1</option>
<option value="2">2</option>
<option value="3">3</option>
</select>
</div>
<img id="screen" src="/stream?mon=1">
<script>
const img = document.getElementById('screen');
const sel = document.getElementById('mon');

sel.addEventListener('change', () => {
    img.src = "/stream?mon=" + sel.value + "&t=" + Date.now();
});

img.addEventListener('click', e => {
    const r = img.getBoundingClientRect();
    const x = (e.clientX - r.left) / r.width;
    const y = (e.clientY - r.top) / r.height;
    fetch('/mouse', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({x:x,y:y,mon:sel.value})
    });
});

window.addEventListener('keydown', e => {
    fetch('/key', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({k:e.key})
    });
});
</script>
</body>
</html>
"""

def stream_gen(mon):
    with mss.mss() as sct:
        monitor = sct.monitors[int(mon)]
        while True:
            with lock:
                img = sct.grab(monitor)
            p = Image.frombytes('RGB', img.size, img.rgb)
            b = io.BytesIO()
            p.save(b, format='JPEG', quality=60)
            frame = b.getvalue()
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            time.sleep(0.05)

@app.route("/")
def index():
    return render_template_string(html)

@app.route("/stream")
def stream():
    mon = request.args.get("mon", "1")
    return Response(stream_gen(mon), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/mouse", methods=["POST"])
def mouse():
    d = request.get_json()
    mon = int(d["mon"])
    x = float(d["x"])
    y = float(d["y"])
    with mss.mss() as sct:
        m = sct.monitors[mon]
    absx = int(m["left"] + m["width"] * x)
    absy = int(m["top"] + m["height"] * y)
    with lock:
        pyautogui.click(absx, absy)
    return "ok"

@app.route("/key", methods=["POST"])
def key():
    k = request.get_json()["k"]
    m = {
        "Enter":"enter","Backspace":"backspace","Tab":"tab","Escape":"esc",
        "ArrowUp":"up","ArrowDown":"down","ArrowLeft":"left","ArrowRight":"right",
        "Delete":"delete"
    }
    if k in m:
        k = m[k]
    with lock:
        try: pyautogui.press(k)
        except: pass
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
