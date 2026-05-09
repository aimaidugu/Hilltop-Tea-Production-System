"""
WageCalculator ADT — Hilltop Tea.

Table-driven rate lookup. No if-else chains in business logic.
Internal state is private. Public interface is calculate_daily().
"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import Employee

# ── Module-level constants — never use raw numbers in logic ────────────────
PRODUCTION_TIERS: list[tuple[int, float, int]] = [
    (0, 349, 250),
    (350, 399, 270),
    (400, 499, 300),
    (500, float('inf'), 320),
]
WRAPPING_RATE: int = 100
MIN_CARTONS: int = 0


class WageCalculator:
    """
    ADT for computing Hilltop Tea daily wages.

    Args:
        None

    Usage:
        calc = WageCalculator()
        wage = calc.calculate_daily(employee, cartons=420)
    """

    def __init__(self) -> None:
        self._tiers: list[tuple[int, float, int]] = list(PRODUCTION_TIERS)
        self._wrapping_rate: int = WRAPPING_RATE

    def calculate_daily(self, employee: "Employee", cartons: int) -> float:
        """
        Compute the daily wage for one employee.

        Args:
            employee: Employee model instance. Must have a `group` attribute
                      of value 'production' or 'wrapping'.
            cartons:  Number of cartons. Must be >= 0.

        Returns:
            Daily wage as float (Nigerian Naira).

        Raises:
            ValueError: If cartons < 0.
            ValueError: If employee.group is unrecognised.
        """
        if cartons < MIN_CARTONS:
            raise ValueError(
                f"Cartons must be >= {MIN_CARTONS}. Received: {cartons}"
            )
        if employee.group == 'production':
            return self._production_wage(cartons)
        if employee.group == 'wrapping':
            return float(cartons * self._wrapping_rate)
        raise ValueError(f"Unknown employee group: '{employee.group}'")

    def _production_wage(self, cartons: int) -> float:
        """
        Table-driven tier lookup. Rate × total cartons (not marginal).

        Raises:
            ValueError: If cartons falls outside all defined tiers.
                        This should never happen with the current tier table
                        because the last tier uses float('inf') as upper bound.
                        The error exists to catch tier misconfiguration early.
        """
        for low, high, rate in self._tiers:
            if low <= cartons <= high:
                return float(cartons * rate)
        raise ValueError(
            f"No matching wage tier for {cartons} cartons. "
            f"Check PRODUCTION_TIERS in wage_calculator.py."
        )

    def get_tiers(self) -> list[tuple[int, float, int]]:
        """Return a defensive copy of the production tier table."""
        return list(self._tiers)
