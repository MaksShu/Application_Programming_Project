from config import app
import pytest
from models import Session, engine, BaseModel, Users, Wallets


@pytest.fixture(scope='function')
def wrapper(request):
    Session().close()
    BaseModel.metadata.drop_all(engine)
    BaseModel.metadata.create_all(engine)


@pytest.fixture()
def norm1_c():
    user = {
        "email": "t3@gmail.com",
        "password": "12345678",
        "first_name": "Bohdan",
        "last_name": "Tsisinskyi"
    }
    return user


@pytest.fixture()
def norm2_c():
    user = {
        "email": "t1@gmail.com",
        "password": "12345678",
        "first_name": "Bohdan",
        "last_name": "Tsisinskyi"
    }
    return user


class TestCreateUser:
    @pytest.fixture()
    def without(self):
        user = {
            "email": "t3gmail.com",
            "password": "12345678",
            "first_name": "Bohdan",
            "last_name": "Tsisinskyi"
        }
        return user

    def test_create_user(self, wrapper, norm1_c):
        response = app.test_client().post('/user', json=norm1_c)
        assert response.status_code == 200

    def test_create_user2(self, wrapper, norm2_c):
        response = app.test_client().post('/user', json=norm2_c)
        assert response.status_code == 200

    def test_fail_create(self, norm1_c, wrapper):
        app.test_client().post('/user', json=norm1_c)
        response = app.test_client().post('/user', json=norm1_c)
        assert response.status_code == 400

    def test_fail_val(self, without, wrapper):
        response = app.test_client().post('/user', json=without)
        assert response.status_code == 400


class TestHello:
    @pytest.fixture()
    def hello_world(self):
        response = app.test_client().get('/hello-world')
        return response.status_code

    def test_hello_world(self, hello_world):
        assert hello_world == 200


@pytest.fixture()
def create_user(norm1_c):
    app.test_client().post('/user', json=norm1_c)


@pytest.fixture()
def create_two_users(norm1_c, norm2_c):
    app.test_client().post('/user', json=norm1_c)
    app.test_client().post('/user', json=norm2_c)


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

    def test_login_user(self, wrapper, norm1, create_user):
        json = norm1
        response = app.test_client().get('/user/login', json=json)
        assert response.status_code == 200

    def test_401_login_user(self, fail, wrapper, create_user):
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

    def test_search_user(self, wrapper, norm, create_user):
        session = Session()
        jsons = norm
        us = session.query(Users).filter_by(email=jsons['email']).first()
        res = app.test_client().get('/user/login', json=jsons)
        token = res.json['access_token']
        response = app.test_client().get(f'/user/{us.id}', headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200

    def test_fail_search_user(self, wrapper, norm, create_user):
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

    def test_logout_user(self, norm, wrapper, create_user):
        json = norm
        res = app.test_client().get('/user/login', json=json)
        token = res.json['access_token']
        response = app.test_client().post(f'/user/logout', headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200


class TestUpdateUser:
    @pytest.fixture()
    def norm(self):
        user = {
            "first_name": "Nazar",
            "last_name": "Tsisinskyi"
        }
        return user

    def test_deny_update_user(self, wrapper, norm, create_two_users):
        session = Session()
        us = session.query(Users).filter_by(email="t3@gmail.com").first()
        res = app.test_client().get('/user/login', json={"email": "t1@gmail.com", "password": "12345678"})
        token = res.json['access_token']
        response = app.test_client().put(f'/user/{us.id}', headers={"Authorization": f"Bearer {token}"}, json=norm)
        assert response.status_code == 403

    def test_update_user(self, wrapper, norm, create_user):
        session = Session()
        json = norm
        us = session.query(Users).filter_by(email="t3@gmail.com").first()
        res = app.test_client().get('/user/login', json={"email": "t3@gmail.com", "password": "12345678"})
        token = res.json['access_token']
        response = app.test_client().put(f'/user/{us.id}', headers={"Authorization": f"Bearer {token}"}, json=norm)
        assert response.json['first_name'] == json['first_name']
        assert response.status_code == 200

    def test_fail_update_user(self, wrapper, norm, create_user):
        res = app.test_client().get('/user/login', json={"email": "t3@gmail.com", "password": "12345678"})
        token = res.json['access_token']
        response = app.test_client().put(f'/user/100', headers={"Authorization": f"Bearer {token}"}, json=norm)
        assert response.status_code == 404


@pytest.fixture()
def norm1_wc():
    wallet = {"funds": 100}
    return wallet


@pytest.fixture()
def norm2_wc():
    wallet = {"funds": 100}
    return wallet


class TestCreateWallet:
    @pytest.fixture()
    def fail(self):
        wallet = {"funds": -10}
        return wallet

    def test_create_wallet(self, wrapper, create_two_users, norm1_wc, norm2_wc):
        json = norm1_wc
        res = app.test_client().get('/user/login', json={"email": "t3@gmail.com", "password": "12345678"})
        token = res.json['access_token']
        response = app.test_client().post('/wallet', headers={"Authorization": f"Bearer {token}"}, json=json)
        assert response.status_code == 200
        json2 = norm2_wc
        response = app.test_client().post('/wallet', headers={"Authorization": f"Bearer {token}"}, json=json2)
        assert response.status_code == 200

    def test_fail_wallet(self, wrapper, create_user, fail):
        json = fail
        res = app.test_client().get('/user/login', json={"email": "t3@gmail.com", "password": "12345678"})
        token = res.json['access_token']
        response = app.test_client().post('/wallet', headers={"Authorization": f"Bearer {token}"}, json=json)
        assert response.status_code == 400


@pytest.fixture()
def create_wallet(norm1_wc):
    res = app.test_client().get('/user/login', json={"email": "t3@gmail.com", "password": "12345678"})
    token = res.json['access_token']
    app.test_client().post('/wallet', headers={"Authorization": f"Bearer {token}"}, json=norm1_wc)
    return token


@pytest.fixture()
def create_two_wallets(norm1_wc, norm2_wc):
    res = app.test_client().get('/user/login', json={"email": "t3@gmail.com", "password": "12345678"})
    token = res.json['access_token']
    app.test_client().post('/wallet', headers={"Authorization": f"Bearer {token}"}, json=norm1_wc)
    app.test_client().post('/wallet', headers={"Authorization": f"Bearer {token}"}, json=norm2_wc)
    return token


class TestSearchWallets:
    def test_search_wallets(self, wrapper, create_user, create_wallet):
        token = create_wallet
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

    def test_search_wallet(self, wrapper, create_user, create_wallet, norm1):
        session = Session()
        us = session.query(Users).filter_by(email=norm1['email']).first()
        w = session.query(Wallets).filter_by(user_id=us.id).first()
        token = create_wallet
        response = app.test_client().get(f'/wallet/{w.id}', headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200

    def test_fail_search_wallet(self, wrapper, create_user, norm1):
        json1 = norm1
        res = app.test_client().get('/user/login', json=json1)
        token = res.json['access_token']
        response = app.test_client().get(f'/wallet/100', headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404

    def test_deny_search_wallet(self, wrapper, create_two_users, create_wallet, norm1, norm2):
        session = Session()
        json2 = norm2
        json1 = norm1
        us = session.query(Users).filter_by(email=json1['email']).first()
        w = session.query(Wallets).filter_by(user_id=us.id).first()
        res = app.test_client().get('/user/login', json=json2)
        token = res.json['access_token']
        response = app.test_client().get(f'/wallet/{w.id}', headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 403


class TestUpWallet:
    @pytest.fixture()
    def norm(self):
        wallet = {"funds": 1000}
        return wallet

    def test_update_wallet(self, wrapper, create_user, create_wallet, norm):
        session = Session()
        json = norm
        us = session.query(Users).filter_by(email="t3@gmail.com").first()
        token = create_wallet
        w = session.query(Wallets).filter_by(user_id=us.id).first()
        response = app.test_client().put(f'/wallet/{w.id}', headers={"Authorization": f"Bearer {token}"}, json=json)
        assert response.status_code == 200

    def test_deny_update_wallet(self, wrapper, create_two_users, create_two_wallets, norm):
        session = Session()
        us = session.query(Users).filter_by(email="t3@gmail.com").first()
        w = session.query(Wallets).filter_by(user_id=us.id).first()
        res = app.test_client().get('/user/login', json={"email": "t1@gmail.com", "password": "12345678"})
        token = res.json['access_token']
        response = app.test_client().put(f'/wallet/{w.id}', headers={"Authorization": f"Bearer {token}"})
        session.close()
        assert response.status_code == 403

    def test_fail_update_wallet(self, wrapper, create_user, create_wallet, norm):
        json = norm
        token = create_wallet
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

    def test_make_transfer(self, wrapper, create_user, create_two_wallets, norm):
        json = norm
        token = create_two_wallets
        response = app.test_client().post('/wallet/make-transfer', headers={"Authorization": f"Bearer {token}"},
                                          json=json)
        assert response.status_code == 200

    def test_fail_make_transfer(self, wrapper, fail1, fail2, create_user, create_wallet):
        json1 = fail1
        json2 = fail2
        token = create_wallet
        response = app.test_client().post('/wallet/make-transfer', headers={"Authorization": f"Bearer {token}"},
                                          json=json1)
        assert response.status_code == 404
        response = app.test_client().post('/wallet/make-transfer', headers={"Authorization": f"Bearer {token}"},
                                          json=json2)
        assert response.status_code == 404

    def test_deny_make_transfer(self, wrapper, create_two_users, create_two_wallets, norm):
        json = norm
        res = app.test_client().get('/user/login', json={"email": "t1@gmail.com", "password": "12345678"})
        token = res.json['access_token']
        response = app.test_client().post('/wallet/make-transfer', headers={"Authorization": f"Bearer {token}"},
                                          json=json)
        assert response.status_code == 403

    def test_error_amount(self, wrapper, create_user, create_two_wallets, amount):
        json = amount
        token = create_two_wallets
        response = app.test_client().post('/wallet/make-transfer', headers={"Authorization": f"Bearer {token}"},
                                          json=json)
        assert response.status_code == 403


@pytest.fixture()
def create_transfer(create_two_users, create_two_wallets):
    token = create_two_wallets
    app.test_client().post('/wallet/make-transfer', headers={"Authorization": f"Bearer {token}"},
                           json={"from_wallet_id": 1, "to_wallet_id": 2, "amount": 10})
    return token


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

    def test_get_transfers(self, wrapper, create_transfer, norm):
        session = Session()
        jsons = norm
        us = session.query(Users).filter_by(email=jsons['email']).first()
        w = session.query(Wallets).filter_by(user_id=us.id).first()
        token = create_transfer
        response = app.test_client().get(f'/wallet/{w.id}/transfers', headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200

    def test_get_transfers_not_found(self, wrapper, create_user, create_wallet, norm):
        session = Session()
        jsons = norm
        us = session.query(Users).filter_by(email=jsons['email']).first()
        token = create_wallet
        response = app.test_client().get(f'/wallet/9/transfers', headers={"Authorization": f"Bearer {token}"})
        session.close()
        assert response.status_code == 404

    def test_deny_get_transfer(self, wrapper, create_transfer, norma):
        session = Session()
        jsons = norma
        us = session.query(Users).filter_by(email="t3@gmail.com").first()
        w = session.query(Wallets).filter_by(user_id=us.id).first()
        res = app.test_client().get('/user/login', json=jsons)
        token = res.json['access_token']
        response = app.test_client().get(f'/wallet/{w.id}/transfers', headers={"Authorization": f"Bearer {token}"})
        session.close()
        assert response.status_code == 403


class TestDeleteWallet:
    @pytest.fixture()
    def norm(self):
        user = {"email": "t3@gmail.com", "password": "12345678"}
        return user

    def test_deny_delete_wallet(self, wrapper, create_two_users, create_wallet, norm):
        session = Session()
        us = session.query(Users).filter_by(email="t3@gmail.com").first()
        w = session.query(Wallets).filter_by(user_id=us.id).first()
        res = app.test_client().get('/user/login', json={"email": "t1@gmail.com", "password": "12345678"})
        token = res.json['access_token']
        response = app.test_client().delete(f'/wallet/{w.id}', headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 403

    def test_fail_delete_wallet(self, wrapper, create_user, create_wallet, norm):
        json = norm
        token = create_wallet
        response = app.test_client().delete(f'/wallet/100', headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404

    def test_delete_wallet(self, wrapper, create_user, create_wallet, norm):
        session = Session()
        json = norm
        us = session.query(Users).filter_by(email=json['email']).first()
        w = session.query(Wallets).filter_by(user_id=us.id).first()
        token = create_wallet
        response = app.test_client().delete(f'/wallet/{w.id}', headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200


class TestDeleteUser:
    def test_delete_user(self, wrapper, create_user, create_wallet):
        token = create_wallet
        response = app.test_client().delete('/user', headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
