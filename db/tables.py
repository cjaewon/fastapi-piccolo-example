from piccolo.table import Table
from piccolo.columns import UUID, Varchar, Text, Timestamptz, ForeignKey

from .engine import DB

class User(Table, tablename="users", db=DB):
  id = UUID(primary_key=True)
  user_id = Varchar(length=255, index=True, unique=True)
  hashed_password = Text()
  created_at = Timestamptz()

class Post(Table, tablename="posts", db=DB):
  id = UUID(primary_key=True)
  title = Text()
  body = Text()
  author = ForeignKey(references=User)
  created_at = Timestamptz()