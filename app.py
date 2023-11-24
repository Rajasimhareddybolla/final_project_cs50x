import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup, usd
import datetime

# Configure application
app = Flask(__name__)
# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

user_names = db.execute("SELECT username as name from users")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    # try:
    #     db.execute("CREATE TABLE stocks(user_id INTEGER ,stock_name VARCHAR(255),stock_no INTEGER,transaction_type varchar(255),transaction_date varchar(255),status integer);")
    # except:
    #     pass
    db.execute(f"drop table present{session['user_id']}")
    id = session["user_id"]
    try:
        db.execute(
            f"CREATE TABLE present{id} AS SELECT * FROM stocks where user_id = ? group by stock_name;",
            999999,
        )
    except:
        pass
    pres_stocks = db.execute(
        "select stock_name,transaction_type,stock_no from stocks where user_id =?;", id
    )
    li_went = []
    for i in range(0, len(pres_stocks)):
        stock_name = pres_stocks[i]["stock_name"]
        total_stocks = 0
        if not (stock_name in li_went):
            for k in range(0, len(pres_stocks)):
                if stock_name == pres_stocks[k]["stock_name"]:
                    if pres_stocks[k]["transaction_type"] == "BUY":
                        total_stocks += int(pres_stocks[k]["stock_no"])
                    else:
                        total_stocks -= int(pres_stocks[k]["stock_no"])

            db.execute(
                f"insert into present{id}(user_id,stock_name,stock_no) values (?,?,?);",
                id,
                stock_name,
                total_stocks,
            )
        li_went.append(stock_name)
    remaining = db.execute("SELECT cash FROM users where id =?;", session["user_id"])
    present = {}
    active = []
    stock_price = 0
    stocks = db.execute(f"select * from present{id};")
    for stock in stocks:
        if stock["status"] != 0:
            active.append(stock)
            look = lookup(stock["stock_name"])
            stock_price += look["price"] * stock["stock_no"]
            present[stock["stock_name"]] = int(look["price"])
    return render_template(
        "index.html",
        stocks=active,
        present=present,
        re=remaining[0]["cash"],
        price=round(stock_price, 3),
        total=remaining[0]["cash"] + stock_price,
    )


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")
    else:
        # try:
        #     db.execute(f"drop table present{session['user_id']};")
        # except:
        #     pass
        # try:
        #     db.execute(f"CREATE TABLE present{session['user_id']} AS SELECT * FROM stocks where user_id = ? group by stock_name having ;",session['user_id'])
        # except:
        #     pass
        if not (request.form.get("symbol") or request.form.get("shares")):
            return apology("sorry enter valid input")
        stock = request.form.get("symbol").upper()
        stock_no = request.form.get("shares")
        if not stock_no.isdigit():
            return apology("its wrong", 400)
        try:
            stock_no = int(stock_no)
        except:
            return apology("its wrong", 400)
        stock_details = lookup(stock)
        if not stock_details:
            return apology("not a valid stock")
        cash = db.execute("SELECT cash FROM users WHERE id =?", session["user_id"])
        ammount = stock_details["price"] * stock_no
        if ammount > cash[0]["cash"]:
            return apology("insufficient balance")
        # try:
        #     db.execute("CREATE TABLE stocks(user_id INTEGER ,stock_name VARCHAR(255),stock_no INTEGER,transaction_type varchar(255),transaction_date varchar(255),status integer);")
        # except:
        #     pass
        db.execute(
            "UPDATE users SET cash = (?) where id = (?);",
            int(cash[0]["cash"] - ammount),
            session["user_id"],
        )
        # use status = 0 for sold out and status =1 for right with us
        try:
            db.execute(
                "INSERT INTO stocks(user_id,stock_name,stock_no,transaction_type,transaction_date,status) VALUES (?,?,?,?,?,?);",
                session["user_id"],
                stock,
                stock_no,
                "BUY",
                datetime.datetime.now(),
                1,
            )
            return redirect("/")
        except:
            return apology("some thing went wrong")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    his = db.execute(
        "select * from stocks where user_id = ? order by transaction_date DESC",
        session["user_id"],
    )
    return render_template("history.html", data=his)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        try:
            db.execute(
                f"CREATE TABLE present{session['user_id']} AS SELECT * FROM stocks where user_id = ? group by stock_name;",
                session["user_id"],
            )
        except:
            pass
        # Redirect user to home page
        return redirect("/")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "GET":
        return render_template("qoute.html")
    stock = request.form.get("symbol")
    if not request.form.get("symbol"):
        return apology("Stocks not avaible")
    results = lookup(stock)
    if not results:
        return apology("not found ", 400)
    return render_template(
        "qouted.html", name=results["name"], price=round(results["price"], 2)
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user_completed"""
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        name = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not (name or password or confirmation):
            return apology("try filling all")
        if not request.form.get("password"):
            return apology("sorry not should empty")
        if not request.form.get("confirmation"):
            return apology("sorry not should empty")
        # for i in user_names:
        #     if i["name"]==name:
        #         return apology("SORRY , user already exist login kindley",400)
        if password != confirmation:
            return apology("mismatch of passwords")
        try:
            db.execute(
                "INSERT INTO users(username,hash) VALUES (?,?)",
                name,
                generate_password_hash(password),
            )
        except:
            return apology("sorry user already exist")
        return redirect("/")
    return apology("checking")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "GET":
        id = session["user_id"]
        user = db.execute("SELECT * FROM users WHERE id = ?;", id)
        present = {}
        active = []
        stocks = db.execute(f"select * from present{id}")
        stock_price = 0
        for stock in stocks:
            if stock["status"] != 0:
                active.append(stock)
                look = lookup(stock["stock_name"])
                stock_price += look["price"]
                present[stock["stock_name"]] = round(look["price"], 1)
        remaining = db.execute("SELECT cash FROM users where id =?", session["user_id"])
        return render_template(
            "sell.html",
            stocks=active,
            present=present,
            re=remaining[0]["cash"],
            price=stock_price,
        )
    if request.method == "POST":
        sale = request.form.get("symbol")
        no = int(request.form.get("shares"))
        id = session["user_id"]
        stocks = db.execute(
            "SELECT * FROM stocks WHERE user_id=? group by stock_name order by transaction_date DESC ;",
            id,
        )
        present = db.execute(
            f"SELECT stock_name,stock_no from present{session['user_id']};"
        )
        for sa in present:
            if sale == sa["stock_name"]:
                if no < 0 or no > sa["stock_no"]:
                    return apology("its not the right way")
                db.execute(
                    "INSERT INTO stocks(user_id,stock_name,stock_no,transaction_type,transaction_date,status) VALUES (?,?,?,?,?,?);",
                    session["user_id"],
                    sale,
                    no,
                    "SELL",
                    datetime.datetime.now(),
                    0,
                )
                money = lookup(sa["stock_name"])
                money_got = money["price"] * no
                money_lis = db.execute(
                    "select cash from users where id =?;", session["user_id"]
                )
                money_have = money_lis[0]["cash"]
                db.execute(
                    "update users set cash =? where id = ?;",
                    money_have + money_got,
                    session["user_id"],
                )
        return redirect("/")
