from fastapi import FastAPI
from contextlib import asynccontextmanager
from routes import users, posts
from db.tables import User, Post

@asynccontextmanager
async def lifespan(app: FastAPI):
  await User.create_table(if_not_exists=True)
  await Post.create_table(if_not_exists=True)
  
  yield

app = FastAPI(lifespan=lifespan)

app.include_router(users.router)
app.include_router(posts.router)

