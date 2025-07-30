from databases import Database
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://tricky_user_dev:MGTGZWyHmlCcFDd5U6RXuQugXCBlOWTY@dpg-d256537gi27c73bntfk0-a.oregon-postgres.render.com/tricky_turns_dev_db")
database = Database(DATABASE_URL)
