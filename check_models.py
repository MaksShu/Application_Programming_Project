from models import *

session = Session()

user1 = Users(first_name="Bohdan", last_name="Tsisinskyi", email="bohdan.tsisinskyi.kn.2021@lpnu.ua", password=83782992)
user2 = Users(first_name="Ivan", last_name="Dvyliuk", email="ivan.dvyliuk.kn.2021@lpnu.ua", password=78627382)
user3 = Users(first_name="Maksim", last_name="Shurypa", email="maksim.shurypa.kn.2021@lpnu.ua", password=81456415)

wallet1 = Wallets(funds=15000, owner=user1)
wallet2 = Wallets(funds=10000, owner=user2)
wallet3 = Wallets(funds=11111, owner=user3)

transfer1 = Transfers(from_wallet=wallet1, to_wallet=wallet2, amount=100)
transfer2 = Transfers(from_wallet=wallet2, to_wallet=wallet3, amount=110)
transfer3 = Transfers(from_wallet=wallet3, to_wallet=wallet1, amount=150)

session.add(user1)
session.add(user2)
session.add(user3)

session.add(wallet1)
session.add(wallet2)
session.add(wallet3)

session.add(transfer1)
session.add(transfer2)
session.add(transfer3)

session.commit()

print(session.query(Users).all()[0].first_name, session.query(Users).all()[0].last_name)