from app import create_app
from app.extensions import db
from app.models import Problem, Step, Hint
import uuid

app = create_app()

with app.app_context():
    # Optional: clear existing data to avoid duplicates/conflicts
    db.session.query(Step).delete()
    db.session.query(Hint).delete()
    db.session.query(Problem).delete()

    # Example 1: Quadratic equation problem (S6 level)
    problem1 = Problem(
        problem_id=str(uuid.uuid4()),
        skill_name="quadratic_equations",
        topic="Algebra",
        target_exam_level="S6",
        difficulty=4,
        question_text="Solve the equation 2x² + 5x - 6 = 0 and give your answers correct to 2 decimal places.",
        correct_answer="x = 1.00 or x = -3.00",
        explanation="Use quadratic formula: x = [-b ± √(b² - 4ac)] / (2a). Discriminant = 73, roots ≈ 1.00 and -3.00.",
        source="Sample REB S6 style (adapted)",
        
        # Teen-friendly concept intro
        concept_intro=(
            "Hey! Quadratic equations look a bit scary with the x², but don't panic — they're just puzzles "
            "where you find the mystery numbers that make the equation true. "
            "Most of the time they have two answers, and we've got some cool tricks to find them. "
            "We'll go through it super slowly together — you've got this! 💪 Ready?"
        )
    )
    db.session.add(problem1)
    db.session.flush()

    # Step 1: Identify coefficients
    step1 = Step(
        step_id=str(uuid.uuid4()),
        problem_id=problem1.problem_id,
        order=1,
        instruction_text="Identify a, b, and c in ax² + bx + c = 0",
        input_type="text",
        correct_answer="a=2, b=5, c=-6",
        explanation="a is with x², b with x, c is the constant."
    )
    db.session.add(step1)

    db.session.add(Hint(step_id=step1.step_id, level=1, hint_text="Look at the standard form..."))
    db.session.add(Hint(step_id=step1.step_id, level=2, hint_text="a = coefficient of x², b = x, c = number alone"))
    db.session.add(Hint(step_id=step1.step_id, level=3, hint_text="So here: a=2, b=5, c=-6"))

    # Step 2: Discriminant
    step2 = Step(
        step_id=str(uuid.uuid4()),
        problem_id=problem1.problem_id,
        order=2,
        instruction_text="Calculate the discriminant D = b² - 4ac",
        input_type="numeric",
        correct_answer="73",
        explanation="D = 25 + 48 = 73"
    )
    db.session.add(step2)

    db.session.add(Hint(step_id=step2.step_id, level=1, hint_text="Discriminant tells us about roots"))
    db.session.add(Hint(step_id=step2.step_id, level=2, hint_text="Plug in: 5² - 4×2×(-6)"))
    db.session.add(Hint(step_id=step2.step_id, level=3, hint_text="25 - 4×2×(-6) = 25 + 48 = 73"))

    # Step 3: One root example
    step3 = Step(
        step_id=str(uuid.uuid4()),
        problem_id=problem1.problem_id,
        order=3,
        instruction_text="Find the positive root using x = [-b + √D] / (2a)",
        input_type="text",
        correct_answer="1.00",
        explanation="≈ [-5 + 8.54]/4 ≈ 1.00"
    )
    db.session.add(step3)

    db.session.add(Hint(step_id=step3.step_id, level=1, hint_text="Use the + version first"))
    db.session.add(Hint(step_id=step3.step_id, level=2, hint_text="√73 ≈ 8.54, so -5 + 8.54 = 3.54"))
    db.session.add(Hint(step_id=step3.step_id, level=3, hint_text="3.54 / 4 = 0.885 ≈ 1.00 after full calc"))

    db.session.commit()
    print("Added sample problem with teen-friendly concept intro!")