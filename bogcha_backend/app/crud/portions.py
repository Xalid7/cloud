from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.ingredient import Ingredient
from app.models.serve import Serve

def get_usage_report(db: Session):
    result = db.query(
        Ingredient.name,
        func.sum(Serve.amount_used).label("total_used"),
        func.date_trunc('day', Serve.served_at).label("date")
    ).join(Serve, Serve.ingredient_id == Ingredient.id)\
     .group_by(Ingredient.name, func.date_trunc('day', Serve.served_at))\
     .order_by("date").all()

    return [{"name": r[0], "used": r[1], "date": r[2]} for r in result]


def get_delivered_report(db: Session):
    result = db.query(
        Ingredient.name,
        Ingredient.quantity_grams,
        Ingredient.delivered_at
    ).order_by(Ingredient.delivered_at.desc()).all()

    return [{"name": r[0], "quantity": r[1], "date": r[2]} for r in result]
