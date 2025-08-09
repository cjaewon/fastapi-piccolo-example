from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from db.tables import User

router = APIRouter(
  prefix="/users",
  tags=["users"],
)

class CreateUserBody(BaseModel):
  username: str = Field(min_length=3, max_length=16)
  password: str = Field(max_length=100)

@router.post("/", responses={409: {}})
async def create_user(body: CreateUserBody):
  exited = await User().exists().where(User.username == body.username)

  if exited:
    raise HTTPException(status_code=status.HTTP_409_CONFLICT)

  await User(
    {
      User.username: body.username,
      User.hashed_password: User.hash_password(body.password),
    }
  ).save()

  # todo: solve cpu bounding problem in hashing.

class CreateTokenBody(BaseModel):
  username: str = Field(min_length=3, max_length=16)
  password: str = Field(max_length=100)

@router.post("/token", responses={401:{}})
async def create_token(body: CreateTokenBody):
  user = await User().objects().where(User.username == body.username).first()

  if not user:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

  verified = user.verify_password(body.password, user.hashed_password)

  if not verified:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
  
  # todo: create token