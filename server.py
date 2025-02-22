from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from starlette.responses import FileResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def read_root():
    return FileResponse(".build/no.html")

@app.get("/en", response_class=HTMLResponse)
def read_item():
    return FileResponse(".build/en.html")