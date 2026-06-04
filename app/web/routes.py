from flask import render_template, redirect, url_for, request, flash
from app.web import bp
from app.models import Credit
from app import db

# Muestra la tabla con todos los créditos ------------

@bp.get("/")
def list_credits():
    status = request.args.get("status")

    query = Credit.query
    if status:
        query = query.filter_by(status=status)

    credits = query.order_by(Credit.created_at.desc()).all()
    return render_template("credits/list.html", credits=credits, status=status)

# Formulario vacío para crear un crédito nuevo ------

@bp.get("/new")
def new_credit():
    return render_template("credits/form.html", credit=None) #CREACIÓN NO EDICIÓN


# Recibe el formulario enviado y guarda el crédito nuevo -----

@bp.post("/new")
def create_credit():
    credit = Credit(
        client_id   = request.form.get("client_id"),
        client_name = request.form.get("client_name"),
        amount      = float(request.form.get("amount")),
        interest    = float(request.form.get("interest")),
        term_months = int(request.form.get("term_months")),
        status      = "ACTIVO",   
    )
    db.session.add(credit)
    db.session.commit()

    flash("Crédito creado correctamente", "success")

    return redirect(url_for("web.list_credits"))


# Muestra el detalle de un crédito específico
@bp.get("/<int:id>")
def detail_credit(id):
    credit = Credit.query.get_or_404(id)
    return render_template("credits/detail.html", credit=credit)


# Muestra el formulario pre-llenado con los datos actuales del crédito

@bp.get("/<int:id>/edit")
def edit_credit(id):
    credit = Credit.query.get_or_404(id)
    return render_template("credits/form.html", credit=credit)


# Recibe el formulario de edición y guarda los cambios ---------

@bp.post("/<int:id>/edit")
def update_credit(id):
    credit = Credit.query.get_or_404(id)

    # Sobreescribe cada campo del objeto con los valores nuevos del formulario
    
    credit.client_id   = request.form.get("client_id")
    credit.client_name = request.form.get("client_name")
    credit.amount      = float(request.form.get("amount"))
    credit.interest    = float(request.form.get("interest"))
    credit.term_months = int(request.form.get("term_months"))
    credit.status      = request.form.get("status")

    db.session.commit()

    flash("Crédito actualizado", "success")

    return redirect(url_for("web.detail_credit", id=id))


# Muestra la pagina de graficas
@bp.get("/charts")
def charts():
    return render_template("credits/charts.html")


# Elimina un crédito -------------

@bp.post("/<int:id>/delete")
def delete_credit(id):
    credit = Credit.query.get_or_404(id)
    db.session.delete(credit)
    db.session.commit()

    flash("Crédito eliminado", "warning")
    return redirect(url_for("web.list_credits"))
