"""FastAPI app: takes task inputs, runs the calculator, asks Claude for insights."""

from typing import Literal

from dotenv import load_dotenv

load_dotenv()  # must run before importing narrator, which reads CLAUDE_MODEL

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from calculator import calculate_task, calculate_totals
from config import AUTOMATION_EFFICIENCY
from narrator import generate_narrative


class TaskInput(BaseModel):
    description: str = Field(min_length=1, max_length=200)
    hours_per_occurrence: float = Field(gt=0, le=1000)
    frequency: Literal["daily", "weekly", "monthly"]
    hourly_rate: float = Field(gt=0, le=10000)


class CalculateRequest(BaseModel):
    tasks: list[TaskInput] = Field(min_length=3, max_length=5)


app = FastAPI(title="AI ROI Calculator")


@app.post("/api/calculate")
def calculate(request: CalculateRequest) -> dict:
    tasks = [
        {**task.model_dump(), **calculate_task(task.hours_per_occurrence, task.frequency, task.hourly_rate)}
        for task in request.tasks
    ]
    totals = calculate_totals(tasks)
    narrative = generate_narrative(tasks, totals)  # None if Claude is unavailable
    return {
        "tasks": tasks,
        "totals": totals,
        "narrative": narrative,
        "automation_efficiency": AUTOMATION_EFFICIENCY,  # shown on the results page as the assumption
    }


app.mount("/", StaticFiles(directory="static", html=True), name="static")
