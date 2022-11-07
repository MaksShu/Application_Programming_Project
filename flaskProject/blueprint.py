import sqlalchemy
from flask import Blueprint, request, jsonify
import marshmallow
import db_utils
from schemas import *
from models import *

api_blueprint = Blueprint('api', __name__)
StudentID = 1

errors = Blueprint('errors', __name__)


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


@api_blueprint.route('/hello-world')
def hello_world_ex():
    return 'Hello World!'


@api_blueprint.route(f'/hello-world-{StudentID}')
def hello_world():
    return f'Hello World {StudentID}', 200


@api_blueprint.route("/user", methods=["POST"])
def create_user():
    user_data = UserCreate().load(request.json)
    user = db_utils.create_entry(Users, **user_data)
    return jsonify(UserInfo().dump(user))


@api_blueprint.route("/user/<int:user_id>", methods=["GET"])
def get_user_by_id(user_id):
    user = db_utils.get_entry_by_id(Users, user_id)
    return jsonify(UserInfo().dump(user))


@api_blueprint.route("/user/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    user_data = UserUpdate().load(request.json)
    user_updated = db_utils.update_entry(Users, user_id, **user_data)
    return jsonify(UserInfo().dump(user_updated))


@api_blueprint.route("/user/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    db_utils.delete_entry(Users, user_id)
    return jsonify({"code": 200, "message": "OK", "type": "OK"})


@api_blueprint.route("/user/login", methods=["GET"])
def login_user():
    return jsonify({"code": 200, "message": "NOT IMPLEMENTED", "type": "OK"})


@api_blueprint.route("/user/logout", methods=["GET"])
def logout_user():
    return jsonify({"code": 200, "message": "NOT IMPLEMENTED", "type": "OK"})


@api_blueprint.route("/wallet", methods=["POST"])
def create_wallet():
    wallet_data = WalletCreate().load(request.json)
    try:
        db_utils.get_entry_by_id(Users, wallet_data["user_id"])
    except sqlalchemy.exc.NoResultFound:
        response = {
            'error': {
                'code': 404,
                'type': 'NOT_FOUND',
                'message': 'User not found'
            }
        }

        return jsonify(response), 404
    wallet = db_utils.create_entry(Wallets, **wallet_data)
    return jsonify(WalletInfo().dump(wallet))


@api_blueprint.route("/wallet", methods=["GET"])
def get_user_wallets():
    user_id = 4
    wallets = db_utils.get_wallets_by_user_id(user_id)
    return jsonify(WalletInfo().dump(wallets, many=True))


@api_blueprint.route("/wallet/<int:wallet_id>", methods=["GET"])
def get_wallet_by_id(wallet_id):
    wallet = db_utils.get_entry_by_id(Wallets, wallet_id)
    return jsonify(WalletInfo().dump(wallet))


@api_blueprint.route("/wallet/<int:wallet_id>", methods=["PUT"])
def update_wallet(wallet_id):
    wallet_data = WalletUpdate().load(request.json)
    wallet_updated = db_utils.update_entry(Wallets, wallet_id, **wallet_data)
    return jsonify(WalletInfo().dump(wallet_updated))


@api_blueprint.route("/wallet/<int:wallet_id>", methods=["DELETE"])
def delete_wallet(wallet_id):
    db_utils.delete_entry(Wallets, wallet_id)
    return jsonify({"code": 200, "message": "OK", "type": "OK"})


@api_blueprint.route("/wallet/make-transfer", methods=["POST"])
def wallet_make_transfer():
    transfer_data = TransferCreate().load(request.json)

    sender = transfer_data["from_wallet_id"]
    receiver = transfer_data["to_wallet_id"]

    try:
        db_utils.get_entry_by_id(Wallets, sender)
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
def get_transfers(wallet_id):

    try:
        db_utils.get_entry_by_id(Wallets, wallet_id)
    except sqlalchemy.exc.NoResultFound:
        response = {
            'error': {
                'code': 404,
                'type': 'NOT_FOUND',
                'message': 'Wallet not found'
            }
        }

        return jsonify(response), 404

    transfers = db_utils.get_transfers_by_wallet_id(wallet_id)
    return jsonify(TransferInfo().dump(transfers, many=True))
