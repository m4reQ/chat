import fastapi

app = fastapi.FastAPI()

@app.get('/')
async def get_root():
    return {'hello': 'world'}