from flask import Flask, session
import os
from dotenv import load_dotenv
import pusher
from prototype.dao.theme_dao import ThemeDao

app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.secret_key = os.urandom(24)

config = {
    "production": {
        "app_id": "1871612",
        "key": "abf1ef860f34591a41b0",
        "secret": "65390bad08b0c624fc2a",
        "cluster": "ap1",
    },
    "development": {
        "app_id": "1871610",
        "key": "6cfad0eebc0f53ace06d",
        "secret": "93872e0593731d00f767",
        "cluster": "ap1",
    },
}


current_dir = os.path.dirname(os.path.abspath(__file__))

while current_dir and os.path.basename(current_dir) != "COMP693_Green_Mean":
    current_dir = os.path.dirname(current_dir)

dotenv_path = os.path.join(current_dir, ".env")
load_dotenv(dotenv_path)
environment = os.getenv("ENVIRONMENT")

app.env = environment

if environment is None:
    raise ValueError("ENVIRONMENT variable is not set in the .env file.")

if environment not in config:
    raise KeyError(f"Invalid environment: {environment}")


app.pusher_client = pusher.Pusher(
    app_id=config[environment]["app_id"],
    key=config[environment]["key"],
    secret=config[environment]["secret"],
    cluster=config[environment]["cluster"],
    ssl=True,
)

from . import error_controller
from . import auth_controller
from . import home_controller
from . import competition_controller
from . import voting_controller
from . import competitor_controller
from . import voter_controller
from . import management_controller
from . import user_controller
from . import scrutineering_controller
from . import theme_controller