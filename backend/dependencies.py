"""Dependency injection for FastAPI."""
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from geopy.geocoders import Nominatim

from backend.services.datamanipulator import DataManipulator
from backend.services.spending import SpendingService
from backend.services.income import IncomeService
from backend.services.receipt import ReceiptService


@lru_cache
def get_data_manipulator() -> DataManipulator:
    """Get singleton DataManipulator instance."""
    return DataManipulator()


@lru_cache
def get_spending_service() -> SpendingService:
    """Get singleton SpendingService instance."""
    return SpendingService(get_data_manipulator())


@lru_cache
def get_income_service() -> IncomeService:
    """Get singleton IncomeService instance."""
    return IncomeService(get_data_manipulator())


@lru_cache
def get_receipt_service() -> ReceiptService:
    """Get singleton ReceiptService instance."""
    return ReceiptService(get_data_manipulator())


@lru_cache
def get_geolocator() -> Nominatim:
    """Get singleton Nominatim geocoder instance."""
    return Nominatim(user_agent="expenses-dashboard")


# Type aliases for cleaner function signatures
DataManipulatorDep = Annotated[DataManipulator, Depends(get_data_manipulator)]
SpendingServiceDep = Annotated[SpendingService, Depends(get_spending_service)]
IncomeServiceDep = Annotated[IncomeService, Depends(get_income_service)]
ReceiptServiceDep = Annotated[ReceiptService, Depends(get_receipt_service)]
GeolocatorDep = Annotated[Nominatim, Depends(get_geolocator)]


def invalidate_caches():
    """Clear all cached service instances."""
    get_data_manipulator.cache_clear()
    get_spending_service.cache_clear()
    get_income_service.cache_clear()
    get_receipt_service.cache_clear()
    get_geolocator.cache_clear()
