from pyBKT.models import Model
import pandas as pd
from app.extensions import db
from app.models import MasteryState, Interaction, Problem
from datetime import datetime

class BKTService:
    def __init__(self):
        self.model = Model(num_fits=20)

    def update_mastery_from_interactions(self, user_id: str, skill_name: str):
        interactions = (
            Interaction.query
            .join(Problem)
            .filter(Interaction.user_id == user_id, Problem.skill_name == skill_name)
            .order_by(Interaction.timestamp)
            .all()
        )

        if not interactions:
            return 0.0

        data = []
        for inter in interactions:
            data.append({
                'user_id': user_id,
                'skill_name': skill_name,
                'correct': inter.correctness,
                'time': inter.timestamp 
            })

        df = pd.DataFrame(data)

        self.model.fit(data=df)
        preds = self.model.predict_proba(data=df)

        latest_mastery = preds.iloc[-1]['state predictions'] if not preds.empty else 0.0

        state = MasteryState.query.filter_by(user_id=user_id, skill_name=skill_name).first()
        if not state:
            state = MasteryState(user_id=user_id, skill_name=skill_name)
            db.session.add(state)

        state.current_mastery_prob = latest_mastery
        state.last_updated = datetime.utcnow()
        db.session.commit()

        return latest_mastery

    def get_current_mastery(self, user_id: str, skill_name: str) -> float:
        state = MasteryState.query.filter_by(user_id=user_id, skill_name=skill_name).first()
        return state.current_mastery_prob if state else 0.0