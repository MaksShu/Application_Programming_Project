from sqlalchemy import *
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, scoped_session

engine = create_engine("postgresql://postgres:24062004@localhost:5432/pptransfer")

SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)

BaseModel = declarative_base()


class Users(BaseModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(LargeBinary, nullable=False)


class Wallets(BaseModel):
    __tablename__ = "wallets"

    id = Column(Integer, Identity(start=1, cycle=False), primary_key=True, nullable=False)
    funds = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    owner = relationship(Users, foreign_keys=[user_id], backref="wallets", lazy="joined")


class Transfers(BaseModel):
    __tablename__ = "transfers"

    id = Column(Integer, Identity(start=1, cycle=False), primary_key=True, nullable=False)
    from_wallet_id = Column(Integer, ForeignKey('wallets.id'), nullable=False)
    to_wallet_id = Column(Integer, ForeignKey('wallets.id'), nullable=False)
    amount = Column(BigInteger)
    datetime = Column(DateTime, server_default=func.now())

    from_wallet = relationship(Wallets, foreign_keys=[from_wallet_id], backref="transfers_from", lazy="joined")
    to_wallet = relationship(Wallets, foreign_keys=[to_wallet_id], backref="transfers_to", lazy="joined")


class TokenBlocklist(BaseModel):
    __tablename__ = "tokenBlockList"
    id = Column(Integer, primary_key=True)
    jti = Column(String(36), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False)
