from flask import Flask, render_template, redirect, session, url_for, request
from src.auth.service import TodoService
from src.auth.models import UserRequest
from src.services import TravelService
from src.models import UserRequest, PlaceRequest, RecommendedRequest, FavoriteRequest
from uuid import UUID

app = Flask(__name__)
travel_service = TravelService()

@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/login_process", methods=["POST"])
def login_process():
    username = request.form["username"]
    password = request.form["password"]
    row = travel_service.authenticate_user(username, password)
    if row:
        session["user_id"] = str(row["id"])
        return redirect(url_for("dashboard", user_id=str(row["id"])))
    return redirect(url_for("login"))