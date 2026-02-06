from fastapi import FastAPI

app = FastAPI(title="Property Search AI")

@app.get("/")
def health_check():
    return {"status": "ok", "service": "Property Search AI"}
