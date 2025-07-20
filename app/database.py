from databases import Database
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:secret@localhost/tricky")
database = Database(DATABASE_URL)
