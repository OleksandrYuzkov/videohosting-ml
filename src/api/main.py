from fastapi import FastAPI
from src.api.routers import comments, search, recsys

app = FastAPI(
    title='VideoHosting ML Service',
    description='A service for analyzing comments, searching moments in videos, and providing recommendations for a video hosting platform.',
    version='0.1.0',
)

app.include_router(comments.router)
app.include_router(search.router)
app.include_router(recsys.router)

@app.get('/health', tags=['System'])
async def health_check():
    return {'status': 'ok', 'service': 'videohosting-ml'}