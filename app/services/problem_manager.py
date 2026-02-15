from app.extensions import db
from app.models import Problem, MasteryState, Step
from sqlalchemy import func
import random

def get_target_exam_level(class_level: str) -> str:
    if class_level in ["S1", "S2", "S3"]:
        return "S3"
    elif class_level in ["S4", "S5", "S6"]:
        return "S6"
    raise ValueError(f"Invalid class level: {class_level}")


def get_next_problem(user_id: str, class_level: str):
    target_level = get_target_exam_level(class_level)

    weakest = (
        db.session.query(MasteryState.skill_name, func.min(MasteryState.current_mastery_prob))
        .filter(MasteryState.user_id == user_id)
        .group_by(MasteryState.skill_name)
        .order_by(func.min(MasteryState.current_mastery_prob))
        .first()
    )

    skill = weakest[0] if weakest else None

    query = Problem.query.filter(Problem.target_exam_level == target_level)

    if skill:
        query = query.filter(Problem.skill_name == skill)

    if query.count() == 0:
        query = Problem.query.filter(Problem.target_exam_level == target_level)

    problems = query.all()
    if not problems:
        return None

    return random.choice(problems)

def get_next_scaffolded_problem(user_id: str, class_level: str):
    target_level = get_target_exam_level(class_level)

    weakest = (
        db.session.query(MasteryState.skill_name, func.min(MasteryState.current_mastery_prob))
        .filter(MasteryState.user_id == user_id)
        .group_by(MasteryState.skill_name)
        .order_by(func.min(MasteryState.current_mastery_prob))
        .first()
    )
    skill = weakest[0] if weakest else None

    query = Problem.query.filter(Problem.target_exam_level == target_level)
    if skill:
        query = query.filter(Problem.skill_name == skill)

    if query.count() == 0:
        query = Problem.query.filter(Problem.target_exam_level == target_level)

    problem = query.order_by(func.random()).first()
    if not problem:
        return None

    steps = (
        Step.query.filter(Step.problem_id == problem.problem_id)
        .order_by(Step.order)
        .all()
    )

    return problem, steps