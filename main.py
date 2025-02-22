import uvicorn
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

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)