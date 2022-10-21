from sqlalchemy import *
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

engine = create_engine("postgresql://postgres:30062003@localhost:5432/pptransfer")
Session = sessionmaker(bind=engine)

BaseModel = declarative_base()


class Users(BaseModel):
    __tablename__ = "users"

    user_id = Column(Integer, Identity(start=1, cycle=False), primary_key=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(Integer, nullable=False)


class Wallets(BaseModel):
    __tablename__ = "wallets"

    wallet_id = Column(Integer, Identity(start=1, cycle=False), primary_key=True, nullable=False)
    funds = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)

    owner = relationship(Users, foreign_keys=[user_id], backref="wallets", lazy="joined")


class Transfers(BaseModel):
    __tablename__ = "transfers"

    transfer_id = Column(Integer, Identity(start=1, cycle=False), primary_key=True, nullable=False)
    from_wallet_id = Column(Integer, ForeignKey('wallets.wallet_id'), nullable=False)
    to_wallet_id = Column(Integer, ForeignKey('wallets.wallet_id'), nullable=False)
    amount = Column(BigInteger)
    datetime = Column(DateTime, server_default=func.now())

    from_wallet = relationship(Wallets, foreign_keys=[from_wallet_id], backref="transfers_from", lazy="joined")
    to_wallet = relationship(Wallets, foreign_keys=[to_wallet_id], backref="transfers_to", lazy="joined")
