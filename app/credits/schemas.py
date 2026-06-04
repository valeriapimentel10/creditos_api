from marshmallow import Schema, fields, validate

class CreditSchema(Schema):

    id          = fields.Int(dump_only=True)
    client_id   = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    client_name = fields.Str(required=True, validate=validate.Length(min=2, max=120))
    amount      = fields.Float(required=True, validate=validate.Range(min=0.01))
    interest    = fields.Float(required=True, validate=validate.Range(min=0.0, max=100.0))
    term_months = fields.Int(required=True, validate=validate.Range(min=1))
    status      = fields.Str(load_default="ACTIVO")
    created_at  = fields.DateTime(dump_only=True, format="%Y-%m-%d %H:%M") # las fechas las pone la BD
    updated_at  = fields.DateTime(dump_only=True, format="%Y-%m-%d %H:%M")

credit_schema  = CreditSchema()
credits_schema = CreditSchema(many=True)
