import pytest

from calculator import calculate_task, calculate_totals


def test_weekly_task():
    # 2 hrs x 52 weeks = 104 hrs; 104 x $50 = $5,200; 70% saved
    result = calculate_task(2, "weekly", 50)
    assert result == {
        "annual_hours": 104.0,
        "annual_cost": 5200.0,
        "hours_saved": 72.8,
        "cost_saved": 3640.0,
    }


def test_daily_task_uses_working_days():
    # 0.5 hrs x 260 days = 130 hrs; 130 x $40 = $5,200
    result = calculate_task(0.5, "daily", 40)
    assert result["annual_hours"] == 130.0
    assert result["annual_cost"] == 5200.0


def test_monthly_task():
    # 4 hrs x 12 months = 48 hrs; 48 x $100 = $4,800
    result = calculate_task(4, "monthly", 100)
    assert result["annual_hours"] == 48.0
    assert result["cost_saved"] == 3360.0


def test_unknown_frequency_raises():
    with pytest.raises(KeyError):
        calculate_task(1, "yearly", 50)


def test_totals_sum_five_tasks():
    tasks = [calculate_task(2, "weekly", 50) for _ in range(5)]
    totals = calculate_totals(tasks)
    assert totals["annual_hours"] == 520.0
    assert totals["annual_cost"] == 26000.0
    assert totals["hours_saved"] == 364.0
    assert totals["cost_saved"] == 18200.0
