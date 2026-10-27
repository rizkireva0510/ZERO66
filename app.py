from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import random
import os

app = Flask(__name__)

# =========================
# KONFIGURASI
# =========================

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "dev-secret-key"
)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///" + os.path.join(BASE_DIR, "zero66.db")
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# =========================
# DATABASE USER
# =========================

class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    coins = db.Column(
        db.Integer,
        default=1000
    )

    score = db.Column(
        db.Integer,
        default=0
    )


# =========================
# SIMBOL GAME
# =========================

SYMBOLS = [
    "🍒",
    "🍋",
    "⭐",
    "💎",
    "7️⃣"
]


SCORES = {

    "🍒": 100,

    "🍋": 150,

    "⭐": 300,

    "💎": 500,

    "7️⃣": 1000

}


# =========================
# DATABASE
# =========================

with app.app_context():

    db.create_all()


# =========================
# LOGIN
# =========================

@app.route("/")
def login():

    if "user_id" in session:

        return redirect(
            url_for("game")
        )

    return render_template(
        "login.html"
    )


@app.route("/login", methods=["POST"])
def login_process():

    username = request.form.get(
        "username",
        ""
    ).strip()

    if not username:

        return redirect(
            url_for("login")
        )

    username = username[:20]

    # Cari user
    user = User.query.filter_by(
        username=username
    ).first()

    # Jika belum ada
    if user is None:

        user = User(
            username=username,
            coins=1000,
            score=0
        )

        db.session.add(user)

        db.session.commit()

    # Simpan ID user
    session["user_id"] = user.id

    return redirect(
        url_for("game")
    )


# =========================
# GAME
# =========================

@app.route("/game")
def game():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    user = db.session.get(
        User,
        session["user_id"]
    )

    if user is None:

        session.clear()

        return redirect(
            url_for("login")
        )

    return render_template(
        "game.html",
        username=user.username,
        coins=user.coins,
        score=user.score
    )


# =========================
# SPIN
# =========================

@app.route("/spin")
def spin():

    if "user_id" not in session:

        return jsonify({
            "error": "Belum login."
        }), 401

    user = db.session.get(
        User,
        session["user_id"]
    )

    if user is None:

        return jsonify({
            "error": "User tidak ditemukan."
        }), 404

    # Biaya virtual
    spin_cost = 10

    # Cek koin
    if user.coins < spin_cost:

        return jsonify({
            "error": "Koin virtual tidak cukup."
        }), 400

    # Kurangi koin
    user.coins -= spin_cost

    # Generate simbol
    result = [

        random.choice(SYMBOLS),

        random.choice(SYMBOLS),

        random.choice(SYMBOLS)

    ]

    earned_score = 0

    message = "Belum cocok. Coba lagi!"


    # =========================
    # 3 SIMBOL SAMA
    # =========================

    if (
        result[0]
        == result[1]
        == result[2]
    ):

        earned_score = SCORES[
            result[0]
        ]

        message = (
            f"JACKPOT! "
            f"+{earned_score} SCORE 🎉"
        )

        # Bonus koin virtual
        user.coins += 50


    # =========================
    # 2 SIMBOL SAMA
    # =========================

    elif (
        result[0] == result[1]
        or
        result[1] == result[2]
        or
        result[0] == result[2]
    ):

        earned_score = 50

        message = (
            "Dua simbol cocok! "
            "+50 SCORE"
        )

        user.coins += 15


    # Tambahkan score
    user.score += earned_score

    # Simpan database
    db.session.commit()


    return jsonify({

        "result": result,

        "earned_score": earned_score,

        "total_score": user.score,

        "coins": user.coins,

        "message": message

    })


# =========================
# LEADERBOARD
# =========================

@app.route("/leaderboard")
def leaderboard():

    users = User.query.order_by(
        User.score.desc()
    ).limit(10).all()

    return render_template(
        "leaderboard.html",
        users=users
    )


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# =========================
# RUN
# =========================

if __name__ == "__main__":

    app.run(
        debug=True
    )