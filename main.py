import os
import sys
import threading
import uvicorn
import webview
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import yt_dlp

app = FastAPI(title="YT Downloader")

if hasattr(sys, "_MEIPASS"):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")

static_dir = os.path.join(base_path, "static")
templates_dir = os.path.join(base_path, "templates")

app.mount("/static", StaticFiles(directory=static_dir), name="static")

DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def home():
    template_path = os.path.join(templates_dir, "index.html")
    if not os.path.exists(template_path):
        raise HTTPException(
            status_code=404, detail="Archivo HTML index.html no encontrado"
        )

    with open(template_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.post("/download")
async def handle_download(url: str = Form(...), format_type: str = Form(...)):
    if not url:
        raise HTTPException(status_code=400, detail="La URL es obligatoria")

    output_template = os.path.join(DOWNLOAD_DIR, "%(title)s-%(id)s.%(ext)s")

    ydl_opts = {
        "outtmpl": output_template,
        "restrictfilenames": True,
        "noplaylist": True,
    }

    if format_type == "audio":
        ydl_opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        })
    else:
        ydl_opts.update({
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)

        return HTMLResponse(content="""
            <html>
                <head>
                    <meta charset="utf-8">
                    <title>Descarga Completada</title>
                    <style>
                        body { font-family: sans-serif; text-align: center; padding-top: 50px; background-color: #1e1e1e; color: white; }
                        .btn { display: inline-block; padding: 10px 20px; background-color: #0078d4; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }
                    </style>
                </head>
                <body>
                    <h2>¡Éxito! 🎉</h2>
                    <p>El archivo se ha descargado correctamente en tu carpeta de <strong>Descargas</strong> de Windows.</p>
                    <a href="/" class="btn">Descargar otro video</a>
                </body>
            </html>
        """)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al descargar: {str(e)}"
        )


def arrancar_backend():
    uvicorn.run(app, host="127.0.0.1", port=14142, log_level="warning")


if __name__ == "__main__":
    hilo_servidor = threading.Thread(target=arrancar_backend, daemon=True)
    hilo_servidor.start()

    webview.create_window(
        title="YouTube Downloader",
        url="http://127.0.0.1:14142",
        width=600,
        height=700,
        resizable=True,
    )

    webview.start()