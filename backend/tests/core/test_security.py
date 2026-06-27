from app.core.security import hash_password, verify_password


def test_hash_password_verifies_round_trip() -> None:
    hashed = hash_password("Test1234!")
    assert hashed != "Test1234!"
    assert verify_password("Test1234!", hashed) is True


def test_verify_password_rejects_wrong_password() -> None:
    hashed = hash_password("Test1234!")
    assert verify_password("wrong-password", hashed) is False


def test_hash_password_uses_unique_salts() -> None:
    assert hash_password("same") != hash_password("same")


def test_hash_password_handles_passwords_over_72_bytes() -> None:
    # bcrypt only considers the first 72 bytes and raises on longer input, so
    # hashing a long password must not error and must still verify.
    long_password = "a" * 200
    hashed = hash_password(long_password)
    assert verify_password(long_password, hashed) is True
