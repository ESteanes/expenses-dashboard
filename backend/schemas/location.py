"""Pydantic schemas for location data."""
from typing import Optional

from pydantic import BaseModel, Field


class LocationBase(BaseModel):
    """Base schema for locations."""
    location: str = Field(..., alias="Location")
    latitude: Optional[float] = Field(None, alias="Latitude")
    longitude: Optional[float] = Field(None, alias="Longitude")

    class Config:
        populate_by_name = True


class LocationCreate(LocationBase):
    """Schema for creating a location."""
    pass


class LocationUpdate(BaseModel):
    """Schema for updating a location."""
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class Location(LocationBase):
    """Full location entry."""
    pass


class GeocodeRequest(BaseModel):
    """Request for geocoding an address."""
    address: str = Field(..., description="Address to geocode")


class GeocodeResponse(BaseModel):
    """Response from geocoding."""
    address: str
    latitude: float
    longitude: float
    display_name: str
