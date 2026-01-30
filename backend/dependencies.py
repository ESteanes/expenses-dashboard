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


def get_spending_service(
    data_manipulator: Annotated[DataManipulator, Depends(get_data_manipulator)]
) -> SpendingService:
    """Get SpendingService with injected DataManipulator."""
    return SpendingService(data_manipulator)


def get_income_service(
    data_manipulator: Annotated[DataManipulator, Depends(get_data_manipulator)]
) -> IncomeService:
    """Get IncomeService with injected DataManipulator."""
    return IncomeService(data_manipulator)


def get_receipt_service(
    data_manipulator: Annotated[DataManipulator, Depends(get_data_manipulator)]
) -> ReceiptService:
    """Get ReceiptService with injected DataManipulator."""
    return ReceiptService(data_manipulator)


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
    get_geolocator.cache_clear()
