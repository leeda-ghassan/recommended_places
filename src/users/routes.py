from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from src.auth.service import AuthService
from src.auth.models import UserRequest

auth_bp = Blueprint("auth", __name__, template_folder="../../templates")

#this is to instantiate, but the path isn't right i think
auth_service = AuthService(db_path="recommended_places.db")

@auth_bp.route("/login", methods=["GET"])
def login():
    return render_template("login.html")

@auth_bp.route("/login_process", methods=["POST"])
def login_process():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    if not email or not password:
        flash("Email and password are required.", "error")
        return redirect(url_for("auth.login"))

    user = auth_service.authenticate_user(email, password)
    if not user:
        flash("Invalid email or password.", "error")
        return redirect(url_for("auth.login"))

    # save only id in session
    session.clear()
    session["user_id"] = user["id"]
    flash(f"Welcome back, {user['name']}!", "success")
    return redirect(url_for("auth.places", user_id=user["id"]))

@auth_bp.route("/register", methods=["GET"])
def register():
    return render_template("register.html")

@auth_bp.route("/register_process", methods=["POST"])
def register_process():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not name or not email or not password:
        flash("Name, email and password are required.", "error")
        return redirect(url_for("auth.register"))

    user_req = UserRequest(name=name, email=email, password=password)
    created = auth_service.create_user(user_req)
    if not created:
        flash("Email already registered. Try logging in.", "error")
        return redirect(url_for("auth.register"))

    flash("Account created. Please log in.", "success")
    return redirect(url_for("auth.login"))

@auth_bp.route("/places/<user_id>", methods=["GET"])
def places(user_id):
    sess_user_id = session.get("user_id")
    if not sess_user_id or sess_user_id != user_id:
        flash("Please log in to continue.", "error")
        return redirect(url_for("auth.login"))

    user = auth_service.get_user_by_id(user_id)
    return render_template("places.html", user=user) #temprary template

@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))