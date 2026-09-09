from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from model import TravelRequestModel
import json
from pydantic import BaseModel
from datetime import date, datetime
from services.weather import fetch_weather
from services.places import fetch_places
from services.currency import fetch_currency_rates

stream_router = APIRouter(
    prefix="/stream",
    tags=["Travel Plan Stream"],
)


def _jsonable(value):
    if isinstance(value, BaseModel):
        return value.model_dump()
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    return value


def format_sse(data: str, event: str = None) -> str:
    json_data = json.dumps(_jsonable(data))
    return (
        f"data: {json_data}\n\n"
        if event is None
        else f"event: {event}\ndata: {json_data}\n\n"
    )


async def stream_generator(travel_request: TravelRequestModel):
    yield format_sse({"message": "Starting travel plan aggregation..."}, event="start")
    yield format_sse({"message": "Fetching weather data..."}, event="weather")
    weather_data = await fetch_weather(
        destination=travel_request.destination,
        start_date=travel_request.start_date,
        end_date=travel_request.end_date,
    )
    yield format_sse({"weather_data": weather_data}, event="weather_complete")
    yield format_sse({"message": "Fetching travel options..."}, event="options")
    places_data = await fetch_places(travel_request.destination)
    yield format_sse({"places_data": places_data}, event="options_complete")

    yield format_sse({"message": "Fetching currency data..."}, event="currency")
    currency_data = await fetch_currency_rates(travel_request.base_currency)
    yield format_sse({"currency_data": currency_data}, event="currency_complete")
    yield format_sse({"message": "Travel plan aggregation complete!"}, event="complete")


@stream_router.get("/", response_class=StreamingResponse)
async def stream_travel_plan(
    destination: str, start_date: date, end_date: date, base_currency: str = "INR"
):
    travel_request = TravelRequestModel(
        destination=destination,
        start_date=start_date,
        end_date=end_date,
        base_currency=base_currency,
    )

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

    return StreamingResponse(
        stream_generator(travel_request),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )
