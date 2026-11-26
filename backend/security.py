
import os

from argon2 import PasswordHasher
from argon2.low_level import Type
from argon2.exceptions import (
    InvalidHashError,
    VerificationError,
)

password_hasher = PasswordHasher(
    type=Type.ID,
    time_cost=int(os.getenv("ARGON2_TIME_COST", "3")),
    memory_cost=int(os.getenv("ARGON2_MEMORY_COST", "65536")),
    parallelism=int(os.getenv("ARGON2_PARALLELISM", "2")),
)


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return password_hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False
