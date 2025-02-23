import uvicorn
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import FileResponse

app = FastAPI()


def read_response(request: Request, html_file: str):
    if request.headers.get("Accept") == "application/ld+json":
        return FileResponse(".build/data.json", media_type="application/ld+json")
    if request.headers.get("Accept") == "application/rdf+xml":
        return FileResponse(".build/data.xml", media_type="application/rdf+xml")
    if request.headers.get("Accept") == "text/turtle":
        return FileResponse(".build/data.ttl", media_type="text/turtle")
    return FileResponse(html_file)


@app.get("/")
def read_norwegian(request: Request):
    return read_response(request, html_file=".build/no.html")


@app.get("/en")
def read_english(request: Request):
    return read_response(request, html_file=".build/en.html")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
