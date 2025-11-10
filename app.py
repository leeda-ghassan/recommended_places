from flask import Flask, render_template, redirect, session, url_for, request
from src.auth.service import AuthService
from src.auth.models import UserRequest
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret-key")
auth_service = AuthService(db_path="recommended_places.db")


@app.route("/")
def index():
    return redirect(url_for("login"))
                
@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login_process", methods=["POST"])
def login_process():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = auth_service.authenticate_user(email, password)
        if user:
            session["user_id"] = user["id"]
            return redirect(url_for("places", user_id=user["id"]))
        else:
            flash("Invalid credentials", "error")
            return redirect(url_for("login"))

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/register_process", methods=["POST"])
def register_process():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        user_req = UserRequest(name=name, email=email, password=password)
        created = auth_service.create_user(user_req)
        if created:
            flash("Account created")
            return redirect(url_for("login"))
        else:
            flash("Registration failed")
            return redirect(url_for("register"))

@app.route("/places/<user_id>")
def places(user_id):
    sess_user_id = session.get("user_id")
    if not sess_user_id or sess_user_id != user_id:
        return redirect(url_for("login"))
    return render_template("places.html", user_id=user_id)

if __name__ == "__main__":
    app.run(debug=True)

