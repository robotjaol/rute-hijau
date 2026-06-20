from engine.models import Impact
from engine.config import (
    FUEL_KM_PER_LITER,
    FUEL_PRICE_RUPIAH,
    EMISSION_KG_PER_LITER,
    DAYS_PER_YEAR,
)


def estimate_impact(distance_saved_km: float) -> Impact:
    fuel_saved_liter = distance_saved_km / FUEL_KM_PER_LITER
    cost_per_cycle = round(fuel_saved_liter * FUEL_PRICE_RUPIAH)
    co2_per_cycle = fuel_saved_liter * EMISSION_KG_PER_LITER
    cost_per_year = round(distance_saved_km * DAYS_PER_YEAR / FUEL_KM_PER_LITER * FUEL_PRICE_RUPIAH)
    co2_per_year = round(distance_saved_km * DAYS_PER_YEAR / FUEL_KM_PER_LITER * EMISSION_KG_PER_LITER)

    return Impact(
        distance_saved_km=round(distance_saved_km, 4),
        fuel_saved_liter=round(fuel_saved_liter, 4),
        cost_saved_rupiah_per_cycle=cost_per_cycle,
        cost_saved_rupiah_per_year=cost_per_year,
        co2_saved_kg_per_cycle=round(co2_per_cycle, 4),
        co2_saved_kg_per_year=co2_per_year,
        assumptions={
            "km_per_liter": FUEL_KM_PER_LITER,
            "price_per_liter": FUEL_PRICE_RUPIAH,
            "emission_kg_per_liter": EMISSION_KG_PER_LITER,
            "days_per_year": DAYS_PER_YEAR,
        },
    )
