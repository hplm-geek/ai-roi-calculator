"""Time and cost savings math. Pure functions, no I/O."""

from config import AUTOMATION_EFFICIENCY, FREQUENCY_PER_YEAR


def calculate_task(hours_per_occurrence: float, frequency: str, hourly_rate: float) -> dict:
    """Annualized current cost and savings for one task."""
    annual_hours = hours_per_occurrence * FREQUENCY_PER_YEAR[frequency]
    annual_cost = annual_hours * hourly_rate
    return {
        "annual_hours": round(annual_hours, 1),
        "annual_cost": round(annual_cost, 2),
        "hours_saved": round(annual_hours * AUTOMATION_EFFICIENCY, 1),
        "cost_saved": round(annual_cost * AUTOMATION_EFFICIENCY, 2),
    }


def calculate_totals(task_results: list[dict]) -> dict:
    """Sum the per-task results into overall totals."""
    keys = ["annual_hours", "annual_cost", "hours_saved", "cost_saved"]
    return {key: round(sum(task[key] for task in task_results), 2) for key in keys}
