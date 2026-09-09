import asyncio
from fastapi import APIRouter, status, HTTPException
from model import TravelRequestModel
from services.weather import fetch_weather
from services.places import fetch_places
from services.currency import fetch_currency_rates
from services.cache import cache_stats, clear_cache

planner_router = APIRouter(
    prefix="/plan",
    tags=["Travel Plan"],
)


@planner_router.post("/")
async def create_travel_plan(travel_request: TravelRequestModel):
    """Aggregate weather, curency and places data into a single travel plan"""

    if travel_request.start_date > travel_request.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date must be before end date",
        )

    trip_days = (travel_request.end_date - travel_request.start_date).days
    if trip_days > 14:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trip must be less than 14 days",
        )

    weather_data, places_data, currency_rates = await asyncio.gather(
        fetch_weather(
            destination=travel_request.destination,
            start_date=travel_request.start_date,
            end_date=travel_request.end_date,
        ),
        fetch_places(destination=travel_request.destination),
        fetch_currency_rates(travel_request.base_currency),
    )

    return {
        "message": "Travel plan created successfully",
        "weather_data": weather_data,
        "places_data": places_data,
        "currency_rates": currency_rates,
    }


@planner_router.get("/cache-stats")
async def get_cache_stats():
    """View cache statistics for travel plans"""
    return cache_stats()


@planner_router.delete("/cache")
async def delete_cache():
    """Clear cache for travel plans"""
    clear_cache()
    return {"message": "Cache cleared successfully"}
