from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from app.credits import bp
from app.credits.schemas import credit_schema, credits_schema
from app.models import Credit
from app import db

# Regresa la lista completa de créditos en JSON
@bp.get("/")
def list_credits():
    status = request.args.get("status")
    query = Credit.query
    if status:
        query = query.filter_by(status=status)
    credits = query.order_by(Credit.created_at.desc()).all()
    return jsonify(credits_schema.dump(credits))

# Crea un nuevo crédito con los datos que vienen en el cuerpo JSON
@bp.post("/")
def create_credit():
    try:
        data = credit_schema.load(request.get_json())
    except ValidationError as e:
        return jsonify({"errors": e.messages}), 422

    credit = Credit(**data)
    db.session.add(credit)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"errors": {"client_id": ["Ya existe un crédito con ese ID de cliente"]}}), 409

    return jsonify(credit_schema.dump(credit)), 201


# Regresa un crédito específico por su ID
@bp.get("/<int:id>")
def get_credit(id):
    credit = Credit.query.get_or_404(id)
    return jsonify(credit_schema.dump(credit))

# Actualiza un crédito existente con los datos nuevos
@bp.put("/<int:id>")
def update_credit(id):
    credit = Credit.query.get_or_404(id)

    try:
        data = credit_schema.load(request.get_json())
    except ValidationError as e:
        return jsonify({"errors": e.messages}), 422

    for key, value in data.items():
        setattr(credit, key, value)

    db.session.commit()

    return jsonify(credit_schema.dump(credit))


# Elimina un crédito de la base de datos
@bp.delete("/<int:id>")
def delete_credit(id):
    credit = Credit.query.get_or_404(id)
    db.session.delete(credit)
    db.session.commit()

    return "", 204


# Devuelve total de creditos otorgados agrupados por mes
@bp.get("/stats/monthly")
def monthly_stats():
    from collections import defaultdict
    credits = Credit.query.all()
    counts = defaultdict(int)
    for c in credits:
        counts[c.created_at.strftime("%Y-%m")] += 1
    result = [{"month": k, "total": v} for k, v in sorted(counts.items())]
    return jsonify(result)


@bp.get("/stats/amount-ranges")
def amount_ranges():
    ranges = [
        {"label": "$0 - $5,000",      "min": 0,     "max": 5000},
        {"label": "$5,001 - $20,000",  "min": 5001,  "max": 20000},
        {"label": "$20,001 - $50,000", "min": 20001, "max": 50000},
        {"label": "$50,001+",          "min": 50001, "max": float("inf")},
    ]
    credits = Credit.query.with_entities(Credit.amount).all()
    for r in ranges:
        r["total"] = sum(1 for (a,) in credits if r["min"] <= a <= r["max"])
    return jsonify([{"label": r["label"], "total": r["total"]} for r in ranges])
