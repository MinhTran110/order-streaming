import os
from dotenv import load_dotenv

load_dotenv()

PG = dict(host=os.getenv("PG_HOST"), port=os.getenv("PG_PORT"),
          user=os.getenv("PG_USER"), password=os.getenv("PG_PASSWORD"),
          dbname=os.getenv("PG_DB"))
RW = dict(host=os.getenv("RW_HOST"), port=os.getenv("RW_PORT"),
          user="root", dbname="dev")