from fastapi import FastAPI

app = FastAPI(
    title="Yatra Planner API",
    description="Aggregate travel data from multiple sources to provide single plan with SSE support",
    version="1.0.0",
)


@app.get("/")
async def root():
    return {
        "app": "Yatra Planner API",
        "version": "1.0.0",
        "endpoints": {
            "POST /plan": "Create a travel plan (Aggregated)",
            "GET /plan/stream": "Stream a travel plan (SSE)",
            "GET /plan/cache-stats": "View Cache statistics for travel plans",
            "DELETE /plan/cache": "Clear Cache for travel plans",
        },
    }
