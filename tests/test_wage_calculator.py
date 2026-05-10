"""
Tests for the WageCalculator ADT.

All test cases with exact expected values as specified.
"""
import pytest

from app.models import Employee
from app.wage_calculator import PRODUCTION_TIERS, WageCalculator


class TestWageCalculatorProduction:
    """Test wage calculation for production workers."""

    def test_boundary_zero_cartons(self, seeded_db):
        """Test 0 cartons returns 0 wage."""
        calc = WageCalculator()
        employee = Employee(name='Test', worker_group='production')
        assert calc.calculate_daily(employee, 0) == 0.0

    def test_boundary_one_carton(self, seeded_db):
        """Test 1 carton at lowest tier."""
        calc = WageCalculator()
        employee = Employee(name='Test', worker_group='production')
        assert calc.calculate_daily(employee, 1) == 250.0

    def test_boundary_349_cartons(self, seeded_db):
        """Test 349 cartons at end of first tier."""
        calc = WageCalculator()
        employee = Employee(name='Test', worker_group='production')
        assert calc.calculate_daily(employee, 349) == 349 * 250

    def test_boundary_350_cartons(self, seeded_db):
        """Test 350 cartons at start of second tier."""
        calc = WageCalculator()
        employee = Employee(name='Test', worker_group='production')
        assert calc.calculate_daily(employee, 350) == 350 * 270

    def test_boundary_399_cartons(self, seeded_db):
        """Test 399 cartons at end of second tier."""
        calc = WageCalculator()
        employee = Employee(name='Test', worker_group='production')
        assert calc.calculate_daily(employee, 399) == 399 * 270

    def test_boundary_400_cartons(self, seeded_db):
        """Test 400 cartons at start of third tier."""
        calc = WageCalculator()
        employee = Employee(name='Test', worker_group='production')
        assert calc.calculate_daily(employee, 400) == 400 * 300

    def test_boundary_499_cartons(self, seeded_db):
        """Test 499 cartons at end of third tier."""
        calc = WageCalculator()
        employee = Employee(name='Test', worker_group='production')
        assert calc.calculate_daily(employee, 499) == 499 * 300

    def test_boundary_500_cartons(self, seeded_db):
        """Test 500 cartons at start of fourth tier."""
        calc = WageCalculator()
        employee = Employee(name='Test', worker_group='production')
        assert calc.calculate_daily(employee, 500) == 500 * 320

    def test_large_carton_count(self, seeded_db):
        """Test 1000 cartons at highest tier."""
        calc = WageCalculator()
        employee = Employee(name='Test', worker_group='production')
        assert calc.calculate_daily(employee, 1000) == 1000 * 320


class TestWageCalculatorWrapping:
    """Test wage calculation for wrapping workers."""

    def test_zero_cartons_wrapping(self, seeded_db):
        """Test 0 cartons for wrapping worker."""
        calc = WageCalculator()
        employee = Employee(name='Test', worker_group='wrapping')
        assert calc.calculate_daily(employee, 0) == 0.0

    def test_fifty_cartons_wrapping(self, seeded_db):
        """Test 50 cartons for wrapping worker."""
        calc = WageCalculator()
        employee = Employee(name='Test', worker_group='wrapping')
        assert calc.calculate_daily(employee, 50) == 50 * 100


class TestWageCalculatorErrors:
    """Test error handling in wage calculation."""

    def test_negative_cartons_raises_error(self, seeded_db):
        """Test negative cartons raises ValueError."""
        calc = WageCalculator()
        employee = Employee(name='Test', worker_group='production')
        with pytest.raises(ValueError, match='Cartons must be >= 0'):
            calc.calculate_daily(employee, -1)

    def test_unrecognised_group_raises_error(self, seeded_db):
        """Test unrecognised group raises ValueError."""
        calc = WageCalculator()
        employee = Employee(name='Test', worker_group='production')
        # Manually set invalid group
        employee.worker_group = 'invalid'
        with pytest.raises(ValueError, match='Unknown employee group'):
            calc.calculate_daily(employee, 100)


class TestWageCalculatorImmutability:
    """Test immutability and defensive copying."""

    def test_get_tiers_returns_copy(self, seeded_db):
        """Test get_tiers returns a copy, not reference."""
        calc = WageCalculator()
        tiers = calc.get_tiers()
        original_length = len(tiers)

        # Modify the returned list
        tiers.append((1000, float('inf'), 400))

        # Original should be unchanged
        assert len(calc.get_tiers()) == original_length

    def test_tier_mutation_does_not_affect_calculator(self, seeded_db):
        """Test mutating returned tiers doesn't affect calculator."""
        calc = WageCalculator()
        tiers = calc.get_tiers()

        # Modify a tier
        if tiers:
            tiers[0] = (100, 200, 300)

        # Calculator should still use original tiers
        employee = Employee(name='Test', worker_group='production')
        assert calc.calculate_daily(employee, 100) == 100 * 250

    def test_empty_tiers_raises_error(self, seeded_db):
        """Test empty tier table raises ValueError."""
        calc = WageCalculator()
        # Monkeypatch to empty tiers
        calc._tiers = []

        employee = Employee(name='Test', worker_group='production')
        with pytest.raises(ValueError, match='No matching wage tier'):
            calc.calculate_daily(employee, 100)


class TestWageCalculatorIntegration:
    """Integration tests with real employee objects."""

    def test_production_employee_from_db(self, seeded_db):
        """Test calculation with production employee from database."""
        calc = WageCalculator()
        employee = Employee.query.filter_by(worker_group='production').first()
        assert employee is not None
        wage = calc.calculate_daily(employee, 450)
        assert wage == 450 * 300

    def test_wrapping_employee_from_db(self, seeded_db):
        """Test calculation with wrapping employee from database."""
        calc = WageCalculator()
        employee = Employee.query.filter_by(worker_group='wrapping').first()
        assert employee is not None
        wage = calc.calculate_daily(employee, 75)
        assert wage == 75 * 100
