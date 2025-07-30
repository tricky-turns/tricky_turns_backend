from databases import Database
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://tricky_user_prod:XnOJxq1pENAUO6kvdpzUpXMrhJkDuIUo@dpg-d2565n7diees739v4l3g-a.oregon-postgres.render.com/tricky_turns_prod_db")
database = Database(DATABASE_URL)
