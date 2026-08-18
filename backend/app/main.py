from fastapi import FastAPI, HTTPException

from app.database import test_database_connection

app = FastAPI(title="Meeting Intelligence API")


@app.get("/")
def root():
    return {"message": "Meeting Intelligence API"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/db-health")
def db_health():
    try:
        result = test_database_connection()

        return {
            "status": "connected",
            "database_test": result,
        }

    except Exception as exc:
        return {
            "status": "failed",
            "error_type": type(exc).__name__,
            "error": str(exc),
        }