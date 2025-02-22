import uvicorn
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import FileResponse

app = FastAPI()


@app.get("/")
def read_norwegian(request: Request):
    if request.headers.get("Accept") == "text/turtle":
        return FileResponse(".build/data.ttl", media_type="text/turtle")
    return FileResponse(".build/no.html")


@app.get("/en")
def read_english(request: Request):
    if request.headers.get("Accept") == "text/turtle":
        return FileResponse(".build/data.ttl", media_type="text/turtle")
    return FileResponse(".build/en.html")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
