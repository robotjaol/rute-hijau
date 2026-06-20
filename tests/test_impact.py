import pytest
from engine.impact import estimate_impact
from engine.config import FUEL_KM_PER_LITER, FUEL_PRICE_RUPIAH, EMISSION_KG_PER_LITER, DAYS_PER_YEAR


def test_impact_zero_savings():
    impact = estimate_impact(0.0)
    assert impact.fuel_saved_liter == pytest.approx(0.0)
    assert impact.cost_saved_rupiah_per_cycle == 0
    assert impact.co2_saved_kg_per_cycle == pytest.approx(0.0)
    assert impact.cost_saved_rupiah_per_year == 0
    assert impact.co2_saved_kg_per_year == 0


def test_impact_fuel_calculation():
    distance = 10.0
    impact = estimate_impact(distance)
    expected_liter = distance / FUEL_KM_PER_LITER
    assert impact.fuel_saved_liter == pytest.approx(expected_liter, rel=1e-4)


def test_impact_cost_per_cycle():
    distance = 10.0
    impact = estimate_impact(distance)
    expected_cost = round((distance / FUEL_KM_PER_LITER) * FUEL_PRICE_RUPIAH)
    assert impact.cost_saved_rupiah_per_cycle == expected_cost


def test_impact_co2_per_cycle():
    distance = 10.0
    impact = estimate_impact(distance)
    expected_co2 = (distance / FUEL_KM_PER_LITER) * EMISSION_KG_PER_LITER
    assert impact.co2_saved_kg_per_cycle == pytest.approx(expected_co2, rel=1e-4)


def test_impact_per_year_equals_per_cycle_times_days():
    distance = 10.0
    impact = estimate_impact(distance)
    expected_cost_year = round((distance / FUEL_KM_PER_LITER) * FUEL_PRICE_RUPIAH * DAYS_PER_YEAR)
    assert impact.cost_saved_rupiah_per_year == expected_cost_year


def test_impact_assumptions_present():
    impact = estimate_impact(5.0)
    assert "km_per_liter" in impact.assumptions
    assert "price_per_liter" in impact.assumptions
    assert "emission_kg_per_liter" in impact.assumptions
    assert "days_per_year" in impact.assumptions
