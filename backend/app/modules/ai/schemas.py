from pydantic import BaseModel


class BusinessInsight(BaseModel):
    problem_summary: str
    data_availability_check: str
    key_issue: str
    simple_insight: str
    recommended_action: list[str]


class BusinessException(BaseModel):
    issue: str
    reason: str
    business_impact: str
    recommended_action: str


class BusinessHealth(BaseModel):
    sales_performance: str
    profit_performance: str
    inventory_health: str
    production_efficiency: str
    employee_attendance: str
    payroll_costs: str
    exceptions: list[BusinessException]


class DailyBrief(BaseModel):
    business_summary: str
    key_metrics: list[str]
    important_alerts: list[str]
    recommended_actions: list[str]
