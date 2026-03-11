import os
from flask import Blueprint, request, jsonify, send_file, abort
from app.extensions import db
from app.models import Hint, Step, User, Problem, Interaction, MasteryState
from app.services.problem_manager import get_next_problem, get_next_scaffolded_problem
from app.services.bkt_service import BKTService
import uuid

api_bp = Blueprint('api', __name__)
bkt_service = BKTService()


@api_bp.route('/users/register', methods=['POST'])
def register_user():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    class_level = data.get('class_level')

    if not all([name, email, class_level]):
        return jsonify({'error': 'Missing fields'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 409

    user = User(
        user_id=str(uuid.uuid4()),
        name=name,
        email=email,
        class_level=class_level.upper()
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'user_id': user.user_id,
        'name': user.name,
        'class_level': user.class_level
    }), 201


@api_bp.route('/problems/next', methods=['POST'])
def get_next():
    data = request.get_json()
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({'error': 'user_id required'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    problem, steps = get_next_scaffolded_problem(user_id, user.class_level)

    if not problem:
        return jsonify({'error': 'No problems available'}), 404

    steps_data = []
    for step in steps:
        hints = Hint.query.filter(Hint.step_id == step.step_id).order_by(Hint.level).all()
        steps_data.append({
            'step_id': step.step_id,
            'order': step.order,
            'instruction_text': step.instruction_text,
            'input_type': step.input_type,
            'explanation': step.explanation,  
            'hints': [{'level': h.level, 'text': h.hint_text} for h in hints]
        })

    return jsonify({
        'problem_id': problem.problem_id,
        'skill_name': problem.skill_name,
        'topic': problem.topic,
        'full_question_text': problem.question_text,
        'source': problem.source,
        'target_exam_level': problem.target_exam_level,
        'concept_intro': problem.concept_intro,          
        'steps': steps_data,
        'final_correct_answer': problem.correct_answer,
        'final_explanation': problem.explanation
    })

@api_bp.route('/interactions/submit', methods=['POST'])
def submit_interaction():
    data = request.get_json() or {}

    user_id = data.get('user_id')
    problem_id = data.get('problem_id')
    step_id = data.get('step_id')
    correctness = data.get('correctness')
    hints_used = data.get('hints_used', 0)
    time_taken = data.get('time_taken', 0.0)

    if not user_id:
        return jsonify({"success": False, "error": "user_id is required"}), 400

    skill_name = None
    resolved_problem_id = problem_id

    with db.session.no_autoflush:
        if step_id:
            step = Step.query.get(step_id)
            if not step:
                return jsonify({"success": False, "error": "Invalid step_id"}), 400
            resolved_problem_id = step.problem_id

        if not resolved_problem_id:
            return jsonify({"success": False, "error": "problem_id is required (or provide a valid step_id)"}), 400

        problem = Problem.query.get(resolved_problem_id)
        if not problem:
            return jsonify({"success": False, "error": "Invalid problem_id"}), 400

        skill_name = problem.skill_name

    interaction = Interaction(
        user_id=user_id,
        problem_id=resolved_problem_id,
        step_id=step_id,
        correctness=correctness,
        hints_used=hints_used,
        time_taken=time_taken,
    )
    db.session.add(interaction)

    new_mastery = None
    if skill_name:
        new_mastery = bkt_service.update_mastery_from_interactions(user_id, skill_name)
    
    db.session.commit()

    return jsonify({"success": True, "new_mastery": new_mastery}), 200


@api_bp.route('/users/<user_id>/mastery', methods=['GET'])
def get_user_mastery(user_id):
    user = User.query.get(user_id)
    if not user:
        abort(404, description="User not found")

    mastery_records = MasteryState.query.filter_by(user_id=user_id).all()
    if not mastery_records:
        return jsonify({"mastery": [], "message": "No mastery data yet"}), 200

    result = []
    for record in mastery_records:
        skill = record.skill_name

        interactions_count = (
            Interaction.query
            .join(Problem, Interaction.problem_id == Problem.problem_id)
            .filter(Interaction.user_id == user_id, Problem.skill_name == skill)
            .count()
        )

        # Simple delta: compare to a default baseline (or store an initial value in DB if you want)
        baseline = 0.3
        delta = record.current_mastery_prob - baseline

        result.append({
            "skill_name": skill,
            "mastery_prob": round(record.current_mastery_prob * 100, 1),
            "delta": round(delta * 100, 1),
            "last_updated": record.last_updated.isoformat() if record.last_updated else None,
            "interactions_count": interactions_count
        })

    result.sort(key=lambda x: x["delta"], reverse=True)
    return jsonify({"mastery": result}), 200

@api_bp.route('/openapi.yaml', methods=['GET'])
def openapi_spec():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    spec_path = os.path.join(project_root, 'openapi.yaml')
    return send_file(spec_path, mimetype='application/yaml')

@api_bp.route('/docs', methods=['GET'])
def swagger_ui():
    html = """<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8"/>
    <title>API Docs</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.18.3/swagger-ui.css"/>
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.18.3/swagger-ui-bundle.min.js"></script>
    <script>
      window.ui = SwaggerUIBundle({ url: 'openapi.yaml', dom_id: '#swagger-ui' });
    </script>
  </body>
</html>"""
    return html