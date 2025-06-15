from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def index():
    return {"status": "🛡️ Vault API is live"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("serve:app", host="0.0.0.0", port=8000)
