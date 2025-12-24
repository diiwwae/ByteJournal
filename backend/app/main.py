from fastapi import FastAPI
from app.api import auth, articles, batch_import, categories, comments, stats

app = FastAPI(title="BitJournal MVP")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(articles.router, prefix="/articles", tags=["articles"])
app.include_router(batch_import.router, prefix="/api/batch-import", tags=["batch-import"])
app.include_router(categories.router, prefix="/categories", tags=["categories"])
app.include_router(comments.router, prefix="/comments", tags=["comments"])
app.include_router(stats.router, prefix="/stats", tags=["stats"])
