from fastapi import FastAPI
from app.api import auth, articles

app = FastAPI(title="BitJournal MVP")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(articles.router, prefix="/articles", tags=["articles"])
