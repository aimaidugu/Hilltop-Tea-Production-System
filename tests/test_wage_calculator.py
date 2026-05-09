"""
Tests for the WageCalculator ADT.

All test cases with exact expected values as specified.
"""
import pytest

from app.wage_calculator import PRODUCTION_TIERS, WRAPPING_RATE, WageCalculator


class TestWageCalculator:
    """Test suite for WageCalculator functionality."""

    def test_production_boundary_0_cartons(self, seeded_db):
        """Test boundary: 0 cartons returns 0 wage."""
        calc = WageCalculator()
        emp = seeded_db.query(Employee).filter_by(group='production').first()
        wage = calc.calculate_daily(emp, 0)
        assert wage == 0.0

    def test_production_boundary_1_carton(self, seeded_db):
        """Test boundary: 1 carton at tier 1 rate."""
        calc = WageCalculator()
        emp = seeded_db.query(Employee).filter_by(group='production').first()
        wage = calc.calculate_daily(emp, 1)
        assert wage == 250.0

    def test_production_boundary_349_cartons(self, seeded_db):
        """Test boundary: 349 cartons at tier 1 rate."""
        calc = WageCalculator()
        emp = seeded_db.query(Employee).filter_by(group='production').first()
        wage = calc.calculate_daily(emp, 349)
        assert wage == 349 * 250

    def test_production_boundary_350_cartons(self, seeded_db):
        """Test boundary: 350 cartons at tier 2 rate."""
        calc = WageCalculator()
        emp = seeded_db.query(Employee).filter_by(group='production').first()
        wage = calc.calculate_daily(emp, 350)
        assert wage == 350 * 270

    def test_production_boundary_399_cartons(self, seeded_db):
        """Test boundary: 399 cartons at tier 2 rate."""
        calc = WageCalculator()
        emp = seeded_db.query(Employee).filter_by(group='production').first()
        wage = calc.calculate_daily(emp, 399)
        assert wage == 399 * 270

    def test_production_boundary_400_cartons(self, seeded_db):
        """Test boundary: 400 cartons at tier 3 rate."""
        calc = WageCalculator()
        emp = seeded_db.query(Employee).filter_by(group='production').first()
        wage = calc.calculate_daily(emp, 400)
        assert wage == 400 * 300

    def test_production_boundary_499_cartons(self, seeded_db):
        """Test boundary: 499 cartons at tier 3 rate."""
        calc = WageCalculator()
        emp = seeded_db.query(Employee).filter_by(group='production').first()
        wage = calc.calculate_daily(emp, 499)
        assert wage == 499 * 300

    def test_production_boundary_500_cartons(self, seeded_db):
        """Test boundary: 500 cartons at tier 4 rate."""
        calc = WageCalculator()
        emp = seeded_db.query(Employee).filter_by(group='production').first()
        wage = calc.calculate_daily(emp, 500)
        assert wage == 500 * 320

    def test_production_boundary_1000_cartons(self, seeded_db):
        """Test boundary: 1000 cartons at tier 4 rate."""
        calc = WageCalculator()
        emp = seeded_db.query(Employee).filter_by(group='production').first()
        wage = calc.calculate_daily(emp, 1000)
        assert wage == 1000 * 320

    def test_wrapping_flat_rate_0_cartons(self, seeded_db):
        """Test wrapping flat rate: 0 cartons returns 0."""
        calc = WageCalculator()
        emp = seeded_db.query(Employee).filter_by(group='wrapping').first()
        wage = calc.calculate_daily(emp, 0)
        assert wage == 0.0

    def test_wrapping_flat_rate_50_cartons(self, seeded_db):
        """Test wrapping flat rate: 50 cartons at ₦100 each."""
        calc = WageCalculator()
        emp = seeded_db.query(Employee).filter_by(group='wrapping').first()
        wage = calc.calculate_daily(emp, 50)
        assert wage == 50 * WRAPPING_RATE

    def test_negative_cartons_raises_value_error(self, seeded_db):
        """Test negative cartons: expect ValueError."""
        calc = WageCalculator()
        emp = seeded_db.query(Employee).filter_by(group='production').first()
        with pytest.raises(ValueError, match='Cartons must be >= 0'):
            calc.calculate_daily(emp, -1)

    def test_unrecognised_group_raises_value_error(self, seeded_db):
        """Test unrecognised group: expect ValueError."""
        calc = WageCalculator()
        emp = seeded_db.query(Employee).filter_by(group='production').first()
        emp.group = 'invalid'
        with pytest.raises(ValueError, match='Unknown employee group'):
            calc.calculate_daily(emp, 100)

    def test_get_tiers_returns_copy(self):
        """Test get_tiers() returns copy — mutation does not affect calculator."""
        calc = WageCalculator()
        tiers = calc.get_tiers()
        original_len = len(tiers)
        tiers.clear()
        assert len(calc.get_tiers()) == original_len

    def test_tier_fallback_raises_value_error(self, monkeypatch):
        """Test tier fallback raises ValueError when tiers are empty."""
        monkeypatch.setattr('app.wage_calculator.PRODUCTION_TIERS', [])
        calc = WageCalculator()
        emp = type('Employee', (), {'group': 'production'})()
        with pytest.raises(ValueError, match='No matching wage tier'):
            calc.calculate_daily(emp, 100)
