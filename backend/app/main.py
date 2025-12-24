from fastapi import FastAPI
from app.api import auth, articles, batch_import

app = FastAPI(title="BitJournal MVP")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(articles.router, prefix="/articles", tags=["articles"])
app.include_router(batch_import.router, prefix="/api/batch-import", tags=["batch-import"])
