"""Location API endpoints."""
from typing import List

from fastapi import APIRouter, HTTPException
import pandas as pd

from backend.dependencies import SpendingServiceDep, GeolocatorDep
from backend.schemas.location import (
    Location,
    LocationCreate,
    LocationUpdate,
    GeocodeRequest,
    GeocodeResponse,
)

router = APIRouter()


@router.get("", response_model=List[dict])
async def list_locations(service: SpendingServiceDep):
    """Get all locations."""
    return service.location.to_dict(orient='records')


@router.get("/missing")
async def get_missing_locations(service: SpendingServiceDep):
    """Get locations from spending that don't have coordinates."""
    # Get unique locations from spending
    spending_locations = set(service.spending['Location'].dropna().unique())

    # Get locations with coordinates
    location_df = service.location
    locations_with_coords = set(
        location_df[location_df['Latitude'].notna()]['Location'].unique()
    )

    # Find missing
    missing = spending_locations - locations_with_coords

    return [{"location": loc} for loc in sorted(missing)]


@router.post("", response_model=dict)
async def create_location(service: SpendingServiceDep, location: LocationCreate):
    """Create a new location."""
    new_row = pd.DataFrame([{
        "Location": location.location,
        "Latitude": location.latitude,
        "Longitude": location.longitude,
    }])

    service._location = pd.concat([service.location, new_row], ignore_index=True)
    service.save_location()

    return new_row.to_dict(orient='records')[0]


@router.put("/{location_name}")
async def update_location(
    service: SpendingServiceDep,
    location_name: str,
    update: LocationUpdate,
):
    """Update location coordinates."""
    df = service.location.copy()

    # Find the location
    mask = df['Location'] == location_name
    if not mask.any():
        raise HTTPException(status_code=404, detail="Location not found")

    # Update coordinates
    if update.latitude is not None:
        df.loc[mask, 'Latitude'] = update.latitude
    if update.longitude is not None:
        df.loc[mask, 'Longitude'] = update.longitude

    service._location = df
    service.save_location()

    return df[mask].to_dict(orient='records')[0]


@router.post("/geocode", response_model=GeocodeResponse)
async def geocode_address(geolocator: GeolocatorDep, request: GeocodeRequest):
    """Geocode an address using Nominatim."""
    try:
        location = geolocator.geocode(request.address)
        if location is None:
            raise HTTPException(status_code=404, detail="Address not found")

        return GeocodeResponse(
            address=request.address,
            latitude=location.latitude,
            longitude=location.longitude,
            display_name=location.address,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
