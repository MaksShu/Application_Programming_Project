CREATE TABLE users(
	user_id INT NOT NULL GENERATED ALWAYS AS IDENTITY,
	first_name VARCHAR(45) NOT NULL,
	last_name VARCHAR(45) NOT NULL,
	email VARCHAR(100) NOT NULL,
	password INT NOT NULL,
	PRIMARY KEY(user_id)
);

CREATE TABLE wallets(
	wallet_id INT NOT NULL GENERATED ALWAYS AS IDENTITY,
	funds INT,
	user_id INT NOT NULL,
	PRIMARY KEY(wallet_id),
	CONSTRAINT fk_user
	   FOREIGN KEY(user_id)
	    REFERENCES users(user_id)
);

CREATE TABLE transfers(
	transfer_id INT NOT NULL GENERATED ALWAYS AS IDENTITY,
	from_wallet_id INT NOT NULL,
	to_wallet_id INT NOT NULL,
	amount BIGINT,
	datetime TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
	PRIMARY KEY(transfer_id),
	CONSTRAINT fk_from_wallet
	   FOREIGN KEY(from_wallet_id)
	    REFERENCES wallets(wallet_id),
	CONSTRAINT fk_to_wallet
	  FOREIGN KEY(to_wallet_id)
	    REFERENCES wallets(wallet_id)
);