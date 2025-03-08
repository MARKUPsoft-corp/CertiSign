from fastapi import FastAPI

app = FastAPI()

@app.get("/add")
def add(a: float, b: float):
    return {"operation": "addition", "result": a+b}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=80001)
