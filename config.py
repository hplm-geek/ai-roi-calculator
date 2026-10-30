"""Calculation assumptions for the ROI calculator.

Everything the math depends on lives here. Change these values to match
your own assumptions; no other file needs to change.
"""

# Share of a task's time that automation is assumed to save.
# 0.70 means "automation removes 70% of the hours spent on this task."
AUTOMATION_EFFICIENCY = 0.70

# Annualization: how many times per year each frequency occurs.
# "daily" uses 260 working days (52 weeks x 5 days), not 365 calendar days.
FREQUENCY_PER_YEAR = {
    "daily": 260,
    "weekly": 52,
    "monthly": 12,
}
