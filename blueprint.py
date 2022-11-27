import sqlalchemy
from flask import Blueprint, request, jsonify
import marshmallow
from flask_bcrypt import check_password_hash
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity, get_jwt
from datetime import datetime
from datetime import timezone

import db_utils
from schemas import *
from models import *
from config import jwt

api_blueprint = Blueprint('api', __name__)
StudentID = 1
session = Session()

errors = Blueprint('errors', __name__)


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token = session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()

    return token is not None


@errors.app_errorhandler(sqlalchemy.exc.NoResultFound)
def handle_error(error):
    response = {
        'error': {
            'code': 404,
            'type': 'NOT_FOUND',
            'message': 'No row was found for one()'
        }
    }

    return jsonify(response), 404


@errors.app_errorhandler(sqlalchemy.exc.IntegrityError)
def handle_error(error):
    response = {
        'error': {
            'code': 400,
            'type': 'BAD_REQUEST',
            'message': 'Not enough data'
        }
    }

    return jsonify(response), 400


@errors.app_errorhandler(marshmallow.exceptions.ValidationError)
def handle_error(error):
    response = {
        'error': {
            'code': 400,
            'type': 'Validation',
            'message': str(error.args[0])
        }
    }

    return jsonify(response), 400


@api_blueprint.route('/hello-world', methods=["GET"])
def hello_world_ex():
    return 'Hello World!'


@api_blueprint.route(f'/hello-world-{StudentID}')
def hello_world():
    return f'Hello World {StudentID}', 200


# checked
@api_blueprint.route("/user", methods=["POST"])
def create_user():
    user_data = UserCreate().load(request.json)
    user = db_utils.create_entry(Users, **user_data)
    return jsonify(UserInfo().dump(user))


# checked
@api_blueprint.route("/user/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user_by_id(user_id):
    try:
        user = db_utils.get_entry_by_id(Users, user_id)
    except sqlalchemy.exc.NoResultFound:
        response = {
            'error': {
                'code': 404,
                'type': 'NOT_FOUND',
                'message': 'User not found'
            }
        }

        return jsonify(response), 404

    return jsonify(UserInfo().dump(user))


# checked
@api_blueprint.route("/user/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    try:
        user = db_utils.get_entry_by_id(Users, user_id)
    except sqlalchemy.exc.NoResultFound:
        response = {
            'error': {
                'code': 404,
                'type': 'NOT_FOUND',
                'message': 'User not found'
            }
        }

        return jsonify(response), 404
    if user_id != get_jwt_identity():
        return jsonify({'error': "Access denied"}), 403

    user_data = UserUpdate().load(request.json)
    user_updated = db_utils.update_entry(Users, user_id, **user_data)
    return jsonify(UserInfo().dump(user_updated))


# checked
@api_blueprint.route("/user", methods=["DELETE"])
@jwt_required()
def delete_user():
    try:
        db_utils.get_entry_by_id(Users, get_jwt_identity())
    except sqlalchemy.exc.NoResultFound:
        response = {
            'error': {
                'code': 404,
                'type': 'NOT_FOUND',
                'message': 'User not found'
            }
        }

        return jsonify(response), 404

    wallets = session.query(Wallets).filter_by(user_id=get_jwt_identity()).all()
    for wallet in wallets:
        delete_wallet(wallet.id)
    db_utils.delete_entry(Users, get_jwt_identity())
    logout_user()
    return jsonify({"code": 200, "message": "OK", "type": "OK"})


# checked
@api_blueprint.route("/user/login", methods=["GET"])
def login_user():
    userLog = LoginUser().load(request.get_json())
    sys_user = session.query(Users).filter_by(email=userLog['email']).first()
    if not sys_user:
        response = {
            'error': {
                'code': 404,
                'type': 'NOT_FOUND',
                'message': 'User not found'
            }
        }
        return jsonify(response), 404

    if check_password_hash(sys_user.password, userLog['password']):
        return jsonify(access_token=create_access_token(identity=sys_user.id)), 200
    else:
        return jsonify({"Error": "Wrong password"}), 401


# checked
@api_blueprint.route("/user/logout", methods=["POST"])
@jwt_required()
def logout_user():
    jti = get_jwt()["jti"]
    now = datetime.now(timezone.utc)
    session.add(TokenBlocklist(jti=jti, created_at=now))
    session.commit()
    return jsonify(msg="JWT revoked")


# checked
@api_blueprint.route("/wallet", methods=["POST"])
@jwt_required()
def create_wallet():
    user_id = get_jwt_identity()
    wallet_funds = WalletCreate().load(request.json)
    try:
        db_utils.get_entry_by_id(Users, user_id)
    except sqlalchemy.exc.NoResultFound:
        response = {
            'error': {
                'code': 404,
                'type': 'NOT_FOUND',
                'message': 'User not found'
            }
        }

        return jsonify(response), 404

    if wallet_funds["funds"] < 0:
        response = {
            'error': {
                'code': 400,
                'type': 'Validation',
                'message': 'Funds can\'t be negative'
            }
        }

        return jsonify(response), 400
    wallet_data = {
        'funds': wallet_funds['funds'],
        'user_id': user_id
    }
    wallet = db_utils.create_entry(Wallets, **wallet_data)
    return jsonify(WalletInfo().dump(wallet))


# checked
@api_blueprint.route("/wallet", methods=["GET"])
@jwt_required()
def get_user_wallets():
    user_id = get_jwt_identity()
    wallets = db_utils.get_wallets_by_user_id(user_id)
    return jsonify(WalletInfo().dump(wallets, many=True))


# checked
@api_blueprint.route("/wallet/<int:wallet_id>", methods=["GET"])
@jwt_required()
def get_wallet_by_id(wallet_id):
    try:
        wallet = db_utils.get_entry_by_id(Wallets, wallet_id)
    except sqlalchemy.exc.NoResultFound:
        response = {
            'error': {
                'code': 404,
                'type': 'NOT_FOUND',
                'message': 'Wallet not found'
            }
        }

        return jsonify(response), 404

    if wallet.user_id != get_jwt_identity():
        return jsonify({'error': "Access denied"}), 403

    return jsonify(WalletInfo().dump(wallet))


# checked
@api_blueprint.route("/wallet/<int:wallet_id>", methods=["PUT"])
@jwt_required()
def update_wallet(wallet_id):
    try:
        wallet = db_utils.get_entry_by_id(Wallets, wallet_id)
    except sqlalchemy.exc.NoResultFound:
        response = {
            'error': {
                'code': 404,
                'type': 'NOT_FOUND',
                'message': 'Wallet not found'
            }
        }

        return jsonify(response), 404

    if wallet.user_id != get_jwt_identity():
        return jsonify({'error': "Access denied"}), 403

    wallet_data = WalletUpdate().load(request.json)
    wallet_updated = db_utils.update_entry(Wallets, wallet_id, **wallet_data)
    return jsonify(WalletInfo().dump(wallet_updated))


# checked
@api_blueprint.route("/wallet/<int:wallet_id>", methods=["DELETE"])
@jwt_required()
def delete_wallet(wallet_id):
    try:
        wallet = db_utils.get_entry_by_id(Wallets, wallet_id)
    except sqlalchemy.exc.NoResultFound:
        response = {
            'error': {
                'code': 404,
                'type': 'NOT_FOUND',
                'message': 'Wallet not found'
            }
        }

        return jsonify(response), 404

    if wallet.user_id != get_jwt_identity():
        return jsonify({'error': "Access denied"}), 403

    transfers1 = session.query(Transfers).filter_by(from_wallet_id=wallet.id).all()
    for transfer1 in transfers1:
        db_utils.delete_entry(Transfers, transfer1.id)
    transfers2 = session.query(Transfers).filter_by(to_wallet_id=wallet.id).all()
    for transfer2 in transfers2:
        db_utils.delete_entry(Transfers, transfer2.id)
    db_utils.delete_entry(Wallets, wallet_id)
    return jsonify({"code": 200, "message": "OK", "type": "OK"})


@api_blueprint.route("/wallet/make-transfer", methods=["POST"])
@jwt_required()
def wallet_make_transfer():
    transfer_data = TransferCreate().load(request.json)

    sender = transfer_data["from_wallet_id"]
    receiver = transfer_data["to_wallet_id"]

    try:
        wallet = db_utils.get_entry_by_id(Wallets, sender)
    except sqlalchemy.exc.NoResultFound:
        response = {
            'error': {
                'code': 404,
                'type': 'NOT_FOUND',
                'message': 'Sender wallet not found'
            }
        }

        return jsonify(response), 404

    try:
        db_utils.get_entry_by_id(Wallets, receiver)
    except sqlalchemy.exc.NoResultFound:
        response = {
            'error': {
                'code': 404,
                'type': 'NOT_FOUND',
                'message': 'Receiver wallet not found'
            }
        }

        return jsonify(response), 404

    if wallet.user_id != get_jwt_identity():
        return jsonify({'error': "You dont have access to this wallet"}), 403

    if db_utils.get_entry_by_id(Wallets, sender).funds < transfer_data["amount"]:
        response = {
            'error': {
                'code': 403,
                'type': 'NOT_ENOUGH_MONEY',
                'message': 'Sender don\'t have enough money'
            }
        }

        return jsonify(response), 403

    transfer = db_utils.create_entry(Transfers, **transfer_data)

    db_utils.wallet_change_funds(sender, -transfer.amount)
    db_utils.wallet_change_funds(receiver, transfer.amount)

    return jsonify(TransferInfo().dump(transfer))


@api_blueprint.route("/wallet/<int:wallet_id>/transfers", methods=["GET"])
@jwt_required()
def get_transfers(wallet_id):
    try:
        user_wallet = db_utils.get_entry_by_id(Wallets, wallet_id)
    except sqlalchemy.exc.NoResultFound:
        response = {
            'error': {
                'code': 404,
                'type': 'NOT_FOUND',
                'message': 'Wallet not found'
            }
        }

        return jsonify(response), 404

    if user_wallet.user_id != get_jwt_identity():
        return jsonify({'error': "Access denied"}), 403

    transfers = db_utils.get_transfers_by_wallet_id(wallet_id)
    return jsonify(TransferInfo().dump(transfers, many=True))
