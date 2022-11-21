from config import app
import pytest
from models import Session, engine, BaseModel, Users, Wallets


class TestCreateUser:
    @pytest.fixture()
    def norm1(self):
        user = {
            "email": "t3@gmail.com",
            "password": "12345678",
            "first_name": "Bohdan",
            "last_name": "Tsisinskyi"
        }
        return user

    @pytest.fixture()
    def norm2(self):
        user = {
            "email": "t1@gmail.com",
            "password": "12345678",
            "first_name": "Bohdan",
            "last_name": "Tsisinskyi"
        }
        return user

    @pytest.fixture()
    def without(self):
        user = {
            "email": "t3gmail.com",
            "password": "12345678",
            "first_name": "Bohdan",
            "last_name": "Tsisinskyi"
        }
        return user

    @staticmethod
    def create_tables():
        BaseModel.metadata.drop_all(engine)
        BaseModel.metadata.create_all(engine)

    def test_create_user(self, norm1):
        self.create_tables()
        response = app.test_client().post('/user', json=norm1)
        assert response.status_code == 200

    def test_create_user2(self, norm2):
        response = app.test_client().post('/user', json=norm2)
        assert response.status_code == 200

    def test_fail_create(self, norm1):
        response = app.test_client().post('/user', json=norm1)
        assert response.status_code == 400

    def test_fail_val(self, without):
        response = app.test_client().post('/user', json=without)
        assert response.status_code == 400


class TestHello:
    @pytest.fixture()
    def hello_world(self):
        response = app.test_client().get('/hello-world')
        return response.status_code

    def test_hello_world(self, hello_world):
        assert hello_world == 200


class TestLoginUser:
    @pytest.fixture()
    def norm1(self):
        user = {
            "email": "t3@gmail.com",
            "password": "12345678",
        }
        return user

    @pytest.fixture()
    def norm2(self):
        user = {
            "email": "t100@gmail.com",
            "password": "12345678",
        }
        return user

    @pytest.fixture()
    def fail(self):
        user = {
            "email": "t3@gmail.com",
            "password": "4654651",
        }
        return user

    def test_login_user(self, norm1):
        json = norm1
        response = app.test_client().get('/user/login', json=json)
        assert response.status_code == 200

    def test_401_login_user(self, fail):
        json = fail
        response = app.test_client().get('/user/login', json=json)
        assert response.status_code == 401

    def test_fail_login_user(self, norm2):
        json = norm2
        response = app.test_client().get('/user/login', json=json)
        assert response.status_code == 404


class TestHelloStudent:
    @pytest.fixture()
    def hello_student(self):
        response = app.test_client().get('/hello-world-1')
        return response.status_code

    def test_hello_world(self, hello_student):
        assert hello_student == 200


class TestSearchUser:
    @pytest.fixture()
    def norm(self):
        user = {
            "email": "t3@gmail.com",
            "password": "12345678",
        }
        return user

    def test_search_user(self, norm):
        session = Session()
        jsons = norm
        us = session.query(Users).filter_by(email=jsons['email']).first()
        res = app.test_client().get('/user/login', json=jsons)
        token = res.json['access_token']
        response = app.test_client().get(f'/user/{us.id}', headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200

    def test_fail_search_user(self, norm):
        jsons = norm
        res = app.test_client().get('/user/login', json=jsons)
        token = res.json['access_token']
        response = app.test_client().get(f'/user/100', headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404


class TestLogoutUser:
    @pytest.fixture()
    def norm(self):
        user = {
            "email": "t3@gmail.com",
            "password": "12345678",
        }
        return user

    def test_search_user(self, norm):
        json = norm
        res = app.test_client().get('/user/login', json=json)
        token = res.json['access_token']
        response = app.test_client().delete(f'/user/logout', headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200


class TestUpdateUser:
    @pytest.fixture()
    def norm(self):
        user = {
            "first_name": "Nazar",
            "last_name": "Tsisinskyi"
        }
        return user

    def test_deny_update_user(self, norm):
        session = Session()
        us = session.query(Users).filter_by(email="t3@gmail.com").first()
        res = app.test_client().get('/user/login', json={"email": "t1@gmail.com", "password": "12345678"})
        token = res.json['access_token']
        response = app.test_client().put(f'/user/{us.id}', headers={"Authorization": f"Bearer {token}"}, json=norm)
        assert response.status_code == 403

    def test_update_user(self, norm):
        session = Session()
        json = norm
        us = session.query(Users).filter_by(email="t3@gmail.com").first()
        res = app.test_client().get('/user/login', json={"email": "t3@gmail.com", "password": "12345678"})
        token = res.json['access_token']
        response = app.test_client().put(f'/user/{us.id}', headers={"Authorization": f"Bearer {token}"}, json=norm)
        assert response.json['first_name'] == json['first_name']
        assert response.status_code == 200

    def test_fail_update_user(self, norm):
        res = app.test_client().get('/user/login', json={"email": "t3@gmail.com", "password": "12345678"})
        token = res.json['access_token']
        response = app.test_client().put(f'/user/100', headers={"Authorization": f"Bearer {token}"}, json=norm)
        assert response.status_code == 404


class TestCreateWallet:
    @pytest.fixture()
    def norm1(self):
        wallet = {"funds": 100}
        return wallet

    @pytest.fixture()
    def norm2(self):
        wallet = {"funds": 100}
        return wallet

    @pytest.fixture()
    def fail(self):
        wallet = {"funds": -10}
        return wallet

    def test_create_wallet(self, norm1, norm2):
        json = norm1
        res = app.test_client().get('/user/login', json={"email": "t3@gmail.com", "password": "12345678"})
        token = res.json['access_token']
        response = app.test_client().post('/wallet', headers={"Authorization": f"Bearer {token}"}, json=json)
        assert response.status_code == 200
        json2 = norm2
        response = app.test_client().post('/wallet', headers={"Authorization": f"Bearer {token}"}, json=json2)
        assert response.status_code == 200

    def test_fail_wallet(self, fail):
        json = fail
        res = app.test_client().get('/user/login', json={"email": "t3@gmail.com", "password": "12345678"})
        token = res.json['access_token']
        response = app.test_client().post('/wallet', headers={"Authorization": f"Bearer {token}"}, json=json)
        assert response.status_code == 400


class TestSearchWallets:
    @pytest.fixture()
    def norm(self):
        user = {
            "email": "t3@gmail.com",
            "password": "12345678",
        }
        return user

    def test_search_wallets(self, norm):
        jsons = norm
        res = app.test_client().get('/user/login', json=jsons)
        token = res.json['access_token']
        response = app.test_client().get(f'/wallet', headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200


class TestSearchWallet:
    @pytest.fixture()
    def norm1(self):
        user = {
            "email": "t3@gmail.com",
            "password": "12345678",
        }
        return user

    @pytest.fixture()
    def norm2(self):
        user = {
            "email": "t1@gmail.com",
            "password": "12345678",
        }
        return user

    def test_search_wallet(self, norm1):
        session = Session()
        jsons = norm1
        us = session.query(Users).filter_by(email=jsons['email']).first()
        w = session.query(Wallets).filter_by(user_id=us.id).first()
        res = app.test_client().get('/user/login', json=jsons)
        token = res.json['access_token']
        response = app.test_client().get(f'/wallet/{w.id}', headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200

    def test_fail_search_wallet(self, norm1):
        json1 = norm1
        res = app.test_client().get('/user/login', json=json1)
        token = res.json['access_token']
        response = app.test_client().get(f'/wallet/100', headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404

    def test_deny_search_wallet(self, norm1, norm2):
        session = Session()
        json2 = norm2
        json1 = norm1
        us = session.query(Users).filter_by(email=json1['email']).first()
        w = session.query(Wallets).filter_by(user_id=us.id).first()
        res = app.test_client().get('/user/login', json=json2)
        token = res.json['access_token']
        response = app.test_client().get(f'/wallet/{w.id}', headers={"Authorization": f"Bearer {token}"})
        session.close()
        assert response.status_code == 403


class TestUpWallet:
    @pytest.fixture()
    def norm(self):
        wallet = {"funds": 1000}
        return wallet

    def test_update_wallet(self, norm):
        session = Session()
        json = norm
        us = session.query(Users).filter_by(email="t3@gmail.com").first()
        res = app.test_client().get('/user/login', json={"email": "t3@gmail.com", "password": "12345678"})
        token = res.json['access_token']
        w = session.query(Wallets).filter_by(user_id=us.id).first()
        response = app.test_client().put(f'/wallet/{w.id}', headers={"Authorization": f"Bearer {token}"}, json=json)
        assert response.status_code == 200

    def test_deny_update_wallet(self, norm):
        session = Session()
        us = session.query(Users).filter_by(email="t3@gmail.com").first()
        w = session.query(Wallets).filter_by(user_id=us.id).first()
        res = app.test_client().get('/user/login', json={"email": "t1@gmail.com", "password": "12345678"})
        token = res.json['access_token']
        response = app.test_client().put(f'/wallet/{w.id}', headers={"Authorization": f"Bearer {token}"})
        session.close()
        assert response.status_code == 403

    def test_fail_update_wallet(self, norm):
        json = norm
        res = app.test_client().get('/user/login', json={"email": "t3@gmail.com", "password": "12345678"})
        token = res.json['access_token']
        response = app.test_client().put(f'/wallet/100', headers={"Authorization": f"Bearer {token}"}, json=json)
        assert response.status_code == 404


class TestWalletMakeTransfer:
    @pytest.fixture()
    def norm(self):
        transfer = {"from_wallet_id": 1, "to_wallet_id": 2, "amount": 10}
        return transfer

    @pytest.fixture()
    def amount(self):
        transfer = {"from_wallet_id": 1, "to_wallet_id": 2, "amount": 100000}
        return transfer

    @pytest.fixture()
    def fail1(self):
        transfer = {"from_wallet_id": 100, "to_wallet_id": 2, "amount": 10}
        return transfer

    @pytest.fixture()
    def fail2(self):
        transfer = {"from_wallet_id": 1, "to_wallet_id": 100, "amount": 10}
        return transfer

    def test_make_transfer(self, norm):
        json = norm
        res = app.test_client().get('/user/login', json={"email": "t3@gmail.com", "password": "12345678"})
        token = res.json['access_token']
        response = app.test_client().post('/wallet/make-transfer', headers={"Authorization": f"Bearer {token}"},
                                          json=json)
        assert response.status_code == 200

    def test_fail_make_transfer(self, fail1, fail2):
        json1 = fail1
        json2 = fail2
        res = app.test_client().get('/user/login', json={"email": "t3@gmail.com", "password": "12345678"})
        token = res.json['access_token']
        response = app.test_client().post('/wallet/make-transfer', headers={"Authorization": f"Bearer {token}"},
                                          json=json1)
        assert response.status_code == 404
        response = app.test_client().post('/wallet/make-transfer', headers={"Authorization": f"Bearer {token}"},
                                          json=json2)
        assert response.status_code == 404

    def test_deny_make_transfer(self, norm):
        json = norm
        res = app.test_client().get('/user/login', json={"email": "t1@gmail.com", "password": "12345678"})
        token = res.json['access_token']
        response = app.test_client().post('/wallet/make-transfer', headers={"Authorization": f"Bearer {token}"},
                                          json=json)
        assert response.status_code == 403

    def test_error_amount(self, amount):
        json = amount
        res = app.test_client().get('/user/login', json={"email": "t3@gmail.com", "password": "12345678"})
        token = res.json['access_token']
        response = app.test_client().post('/wallet/make-transfer', headers={"Authorization": f"Bearer {token}"},
                                          json=json)
        assert response.status_code == 403


class TestGetTransfers:
    @pytest.fixture()
    def norm(self):
        user = {
            "email": "t3@gmail.com",
            "password": "12345678",
        }
        return user

    @pytest.fixture()
    def norma(self):
        user = {
            "email": "t1@gmail.com",
            "password": "12345678",
        }
        return user

    def test_get_transfers(self, norm):
        session = Session()
        jsons = norm
        us = session.query(Users).filter_by(email=jsons['email']).first()
        w = session.query(Wallets).filter_by(user_id=us.id).first()
        res = app.test_client().get('/user/login', json=jsons)
        token = res.json['access_token']
        response = app.test_client().get(f'/wallet/{w.id}/transfers', headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200

    def test_deny_get_transfer(self, norma):
        session = Session()
        jsons = norma
        us = session.query(Users).filter_by(email="t3@gmail.com").first()
        w = session.query(Wallets).filter_by(user_id=us.id).first()
        res = app.test_client().get('/user/login', json=jsons)
        token = res.json['access_token']
        response = app.test_client().get(f'/wallet/{w.id}/transfers', headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 403


class TestDeleteWallet:
    @pytest.fixture()
    def norm(self):
        user = {"email": "t3@gmail.com", "password": "12345678"}
        return user

    def test_deny_update_wallet(self, norm):
        session = Session()
        us = session.query(Users).filter_by(email="t3@gmail.com").first()
        w = session.query(Wallets).filter_by(user_id=us.id).first()
        res = app.test_client().get('/user/login', json={"email": "t1@gmail.com", "password": "12345678"})
        token = res.json['access_token']
        response = app.test_client().delete(f'/wallet/{w.id}', headers={"Authorization": f"Bearer {token}"})
        session.close()
        assert response.status_code == 403

    def test_fail_delete_wallet(self, norm):
        json = norm
        res = app.test_client().get('/user/login', json=json)
        token = res.json['access_token']
        response = app.test_client().delete(f'/wallet/100', headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404

    def test_delete_wallet(self, norm):
        session = Session()
        json = norm
        us = session.query(Users).filter_by(email=json['email']).first()
        w = session.query(Wallets).filter_by(user_id=us.id).first()
        res = app.test_client().get('/user/login', json=json)
        token = res.json['access_token']
        response = app.test_client().delete(f'/wallet/{w.id}', headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200


class TestDeleteUser:
    @pytest.fixture()
    def norm(self):
        user = {"email": "t3@gmail.com", "password": "12345678"}
        return user

    def test_delete_user(self, norm):
        json = norm
        res = app.test_client().get('/user/login', json=json)
        token = res.json['access_token']
        response = app.test_client().delete('/user', headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
