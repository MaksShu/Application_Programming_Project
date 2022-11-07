from models import *


def create_entry(model_class, *, commit=True, **kwargs):
    session = Session()
    session.expire_on_commit = false
    entry = model_class(**kwargs)
    session.add(entry)
    if commit:
        session.commit()
    return session.query(model_class).order_by(desc(model_class.id)).first()


def get_entry_by_id(model_class, id, **kwargs):
    session = Session()
    return session.query(model_class).filter_by(id=id, **kwargs).one()


def update_entry(model_class, id, *, commit=True, **kwargs):
    session = Session()
    for key, value in kwargs.items():
        session.query(model_class).filter(model_class.id == id).update({key: value})
    if commit:
        session.commit()
    entry = session.query(model_class).filter_by(id=id, **kwargs).one()
    return entry


def delete_entry(model_class, id, commit=True, **kwargs):
    session = Session()
    user = session.query(model_class).filter_by(id=id, **kwargs).one()
    if user != null:
        session.query(model_class).filter_by(id=id, **kwargs).delete()
    if commit:
        session.commit()


def get_wallets_by_user_id(user_id):
    session = Session()
    wallets = session.query(Wallets).filter(Wallets.user_id == user_id).all()
    return wallets


def wallet_change_funds(wallet_id, amount):
    session = Session()
    wallet = session.query(Wallets).filter(Wallets.id == wallet_id).one()
    session.query(Wallets).filter(Wallets.id == wallet_id).update({"funds": wallet.funds + amount})
    session.commit()


def get_transfers_by_wallet_id(wallet_id):
    session = Session()
    transfers = session.query(Transfers).filter(or_(Transfers.from_wallet_id == wallet_id,
                                                    Transfers.to_wallet_id == wallet_id)).all()
    return transfers
