import os
import hmac
import base64
import hashlib
from datetime import datetime, timedelta, timezone
import secrets
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException
from pydantic import AwareDatetime, BaseModel, Field

# --- session ---
# server based session

SESSION_TTL = timedelta(days=7)

def create_session_id(length=32) -> str:
  return secrets.token_urlsafe(length)

class Session(BaseModel):
  user_id: str
  created_at: AwareDatetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))

# note: consider some other store for multi-process environment
session_store: dict[str, Session] = {}

def auth_required(session_id: Annotated[str | None, Cookie()] = None) -> Session:
  if session_id is None:
    raise HTTPException(status_code=401)

  if session_id not in session_store:
    raise HTTPException(status_code=401)

  session = session_store[session_id]
  
  # check session expired
  # todo: re issue session
  if datetime.now(tz=timezone.utc) - session.created_at > SESSION_TTL:
    del session

    raise HTTPException(status_code=401)


  return session

# --- password ---

def hash_password(password: str):
  """
  hash_password generates and returns hashed_password with pbkdf2.
  Note that there are better hash algorithms (argon2id, scrypt) and additional security parts (peeper, rehashing).
  """

  # todo: change hash algorithms to argon2id.

  salt = os.urandom(16)
  iterations = 600000

  hashed_password = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)

  b64_salt = base64.b64encode(salt).decode("ascii").strip()
  b64_hash = base64.b64encode(hashed_password).decode("ascii").strip()

  return f"pbkdf2_sha256${iterations}${b64_salt}${b64_hash}"

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



AuthRequiredDep = Annotated[str, Depends(auth_required)]