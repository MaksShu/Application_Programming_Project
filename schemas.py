from flask_bcrypt import generate_password_hash
from marshmallow import validate, Schema, fields


class UserCreate(Schema):
    email = fields.String(validate=validate.Email())
    password = fields.Function(
        deserialize=lambda obj: generate_password_hash(obj), load_only=True
    )
    first_name = fields.String()
    last_name = fields.String()


class UserInfo(Schema):
    id = fields.Integer()
    email = fields.Email()
    first_name = fields.String()
    last_name = fields.String()


class UserUpdate(Schema):
    email = fields.Email(validate=validate.Email())
    password = fields.Function(
        deserialize=lambda obj: generate_password_hash(obj), load_only=True
    )
    first_name = fields.String()
    last_name = fields.String()


class LoginUser(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)


class WalletCreate(Schema):
    funds = fields.Integer()


class WalletInfo(Schema):
    id = fields.Integer()
    user_id = fields.Integer()
    funds = fields.Integer()


class WalletUpdate(Schema):
    funds = fields.Integer()


class TransferCreate(Schema):
    from_wallet_id = fields.Integer()
    to_wallet_id = fields.Integer()
    amount = fields.Integer()


class TransferInfo(Schema):
    id = fields.Integer()
    from_wallet_id = fields.Integer()
    to_wallet_id = fields.Integer()
    amount = fields.Integer()
    datetime = fields.DateTime()
