from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.backend.api import analytics, factory, miniapp, stores

app = FastAPI(title="Miramax Bonus API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Mini App is served from a Telegram webview origin that varies per client; tighten once the real domain is fixed on VPS.
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analytics.router)
app.include_router(factory.router)
app.include_router(miniapp.router)
app.include_router(stores.router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
