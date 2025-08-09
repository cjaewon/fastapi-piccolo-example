import os
import hmac
import base64
import hashlib

from piccolo.table import Table
from piccolo.columns import UUID, Varchar, Text, Timestamptz, ForeignKey

from .engine import DB

class User(Table, tablename="users", db=DB):
  id = UUID(primary_key=True)
  username = Varchar(length=255, index=True, unique=True)
  hashed_password = Text(secret=True)
  created_at = Timestamptz()

  @staticmethod
  def hash_password(password: str):
    """
    hash_password generates and returns hashed_password with pbkdf2.
    Note that there are better hash algorithms (argon2id, scrypt) and additional security parts (peeper, rehashing).
    """

    salt = os.urandom(16)
    iterations = 600000

    hashed_password = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)

    b64_salt = base64.b64encode(salt).decode("ascii").strip()
    b64_hash = base64.b64encode(hashed_password).decode("ascii").strip()

    return f"pbkdf2_sha256${iterations}${b64_salt}${b64_hash}"

  @staticmethod
  def verify_password(password: str, hashed_password: str) -> bool:
    """
    verify_password verifies that password is correct with hashed_password.
    """
    algorithm, iterations_str, b64_salt, b64_hash = hashed_password.split("$", 3)

    if algorithm != "pbkdf2_sha256":
      raise ValueError("Unsupported password hashing algorithm.")

    iterations = int(iterations_str)
    salt = base64.b64decode(b64_salt)
    hashed_password_bytes = base64.b64decode(b64_hash)

    hashed_checking_password = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)

    return hmac.compare_digest(hashed_checking_password, hashed_password_bytes)
  
class Post(Table, tablename="posts", db=DB):
  id = UUID(primary_key=True)
  title = Text()
  body = Text()
  pk_user_id = ForeignKey(references=User)
  created_at = Timestamptz()