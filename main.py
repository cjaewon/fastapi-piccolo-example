from fastapi import FastAPI
from routes import users, posts

app = FastAPI()

app.include_router(users.router)
app.include_router(posts.router)

