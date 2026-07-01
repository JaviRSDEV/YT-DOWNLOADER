import os
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import yt_dlp

app = FastAPI(title="YT Downloader")

# Montar el directorio de archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def home():
    template_path = os.path.join("templates", "index.html")
    if not os.path.exists(template_path):
        raise HTTPException(status_code=404, detail="Archivo HTML index.html no encontrado")
    
    with open(template_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())
    
@app.post("/download")
async def handle_download(
    url: str = Form(...),
    format_type: str = Form(...)
):
    if not url:
        raise HTTPException(status_code=400, detail="La URL es obligatoria")
    
    output_template = os.path.join(DOWNLOAD_DIR, '%(title)s-%(id)s.%(ext)s')

    ydl_opts = {
        'outtmpl': output_template,
        'restrictfilenames': True,
        'noplaylist': True,  # Evita descargar listas de reproducción completas
    }

    if format_type == "audio":
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',       
            }],
        })
    else:
        ydl_opts.update({
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
        })

    try:
        # Nota: Usamos yt_dlp con guion bajo (_) en Python, no con guion medio (-)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

            if format_type == "audio":
                filename = os.path.splitext(filename)[0] + ".mp3"
            else:
                filename = os.path.splitext(filename)[0] + ".mp4"
        
        return FileResponse(
            path=filename,
            media_type='application/octet-stream',
            filename=os.path.basename(filename)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al descargar: {str(e)}")