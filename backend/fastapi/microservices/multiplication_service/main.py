from fastapi import FastAPI

app = FastAPI()

@app.get("/multiply")
def multiply(a: float, b: float):
    return {"operation": "multiplication", "result": a * b}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)
