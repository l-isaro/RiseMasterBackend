from pyBKT.models import Model
import pandas as pd
from app.extensions import db
from app.models import MasteryState, Interaction, Problem
from datetime import datetime

class BKTService:
    def __init__(self, num_fits: int = 1, max_interactions: int = 200):
        self.num_fits = num_fits
        self.max_interactions = max_interactions

    def update_mastery_from_interactions(self, user_id: str, skill_name: str) -> float:
        interactions = (
            Interaction.query
            .join(Problem, Interaction.problem_id == Problem.problem_id)
            .filter(Interaction.user_id == user_id, Problem.skill_name == skill_name)
            .order_by(Interaction.timestamp.asc())
            .limit(self.max_interactions)
            .all()
        )

        if not interactions:
            return 0.0

        rows = []
        for inter in interactions:
            if inter.correctness is None:
                continue
            rows.append({
                "user_id": str(user_id),
                "skill_name": str(skill_name),
                "correct": int(inter.correctness),
            })

        if not rows:
            return 0.0

        df = pd.DataFrame(rows)

        model = Model(num_fits=self.num_fits)
        model.fit(data=df)

        # ---- prediction (older pyBKT uses predict, not predict_proba) ----
        preds = model.predict(data=df)

        # Try common column names depending on version
        latest_mastery = 0.0
        if preds is not None and not preds.empty:
            for col in ["state_predictions", "state predictions", "mastery", "prob_mastery"]:
                if col in preds.columns:
                    latest_mastery = float(preds.iloc[-1][col])
                    break

        state = MasteryState.query.filter_by(user_id=user_id, skill_name=skill_name).first()
        if not state:
            state = MasteryState(user_id=user_id, skill_name=skill_name)
            db.session.add(state)

        state.current_mastery_prob = latest_mastery
        state.last_updated = datetime.utcnow()

        db.session.flush()
        return latest_mastery