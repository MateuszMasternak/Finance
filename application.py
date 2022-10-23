import os, datetime

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv

from db import Database 

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Take environment variables from .env
load_dotenv()

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure database
db = Database(os.getenv("DB_NAME"))
res = db.cur.execute("SELECT name FROM sqlite_master WHERE name='users'")
if res.fetchone() is None:
    db.cur.execute("CREATE TABLE users ('id' integer PRIMARY KEY NOT NULL, 'username' text NOT NULL, 'hash' text NOT NULL, 'cash' numeric NOT NULL DEFAULT 10000.00 )")
    db.con.commit()
res = db.cur.execute("SELECT name FROM sqlite_master WHERE name='transactions'")
if res.fetchone() is None:
    db.cur.execute("CREATE TABLE transactions ('id' integer PRIMARY KEY NOT NULL, 'user_id' integer NOT NULL, 'symbol' text NOT NULL, 'price' numeric NOT NULL, 'shares' integer NOT NULL, 'time' text NOT NULL)")
    db.con.commit()


# Make sure API key is set
if not os.getenv("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session["user_id"]
    cash = db.cur.execute("SELECT cash FROM users WHERE id=?", (user_id,))
    cash = cash.fetchone()
    transactions = db.cur.execute("SELECT symbol, sum(shares) FROM transactions WHERE user_id = ? GROUP BY symbol", (user_id,))
    transactions = transactions.fetchall()
    transactions_sum = []
    total = cash[0]
    for transaction in transactions:
        shares = transaction[1]
        if shares > 0:
            symbol = transaction[0]
            look = lookup(symbol)
            price = look["price"]
            name = look["name"]
            value = price * transaction[1]
            total += value
            transactions_sum.append([symbol, name, shares, price, value])
    return render_template("index.html", transactions_sum=transactions_sum, cash=cash[0], total=total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        data = lookup(symbol)
        if data == None:
            return apology("must provide existing symbol", 400)
        symbol = data["symbol"]
        name = data["name"]
        price = data["price"]
        shares = request.form.get("shares")
        check = [False, False, False]
        if shares != None:
            check[0] = True
            if shares.isnumeric():
                check[1] = True
                shares = float(shares)
                if shares >= 1 and int(shares) == shares:
                    check[2] = True
        if False in check:
            return apology("must provide positive and not fractional number of shares", 400)
        shares = int(shares)
        user_id = session["user_id"]
        cash = db.cur.execute("SELECT cash FROM users WHERE id = ?", (user_id,))
        cash = cash.fetchone()
        if cash[0] < shares * price:
            return apology("not enough cash", 400)
        cash = cash[0] - shares * price
        db.cur.execute("UPDATE users SET cash = ? WHERE id = ?", (cash, user_id))
        db.con.commit()
        time = datetime.datetime.now()
        time = time.strftime("%Y-%m-%d %H:%M:%S")
        db.cur.execute("INSERT INTO transactions (user_id, symbol, price, shares, time) VALUES (?, ?, ?, ?, ?)", (user_id, symbol, price, shares, time))
        db.con.commit()
        return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]
    transactions = db.cur.execute("SELECT symbol, shares, price, time FROM transactions WHERE user_id = ?", (user_id,))
    transactions = transactions.fetchall()
    return render_template("history.html", transactions=transactions)


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
        username = request.form.get("username")
        user = db.cur.execute("SELECT id, hash FROM users WHERE username = ?", (username,))
        user = user.fetchone()

        # Ensure username exists and password is correct
        print(user)
        if user is None:
            return apology("invalid username and/or password", 403)
        else:
            check_password = check_password_hash(user[1], request.form.get("password"))
            if not check_password:
                return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = user[0]

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
    if request.method == "POST":
        symbol = request.form.get("symbol")
        data = lookup(symbol)
        if data == None:
            return apology("must provide existing symbol", 400)
        return render_template("quoted.html", data=data)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if username == None or password == None or confirmation == None or password != confirmation:
            return apology("must provide username and password which is same in both fields", 400)
        username_check = db.cur.execute("SELECT username from users WHERE username=?", (username,))
        if username_check.fetchone() is not None:
            return apology("that username already exists", 400)
        check_len = False
        if len(password) >= 8 and len(password) <= 12:
            check_len = True
        signs = ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")"]
        check_sign = any(sign in password for sign in signs)
        numbers = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
        check_num = any(num in password for num in numbers)
        if check_len != True or check_sign != True or check_num != True:
            return apology("password should have 8 to 12 characters, one special sign [!@#$%^&*()] and one number [0-9]", 400)


        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        db.cur.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hashed_password))
        db.con.commit()
        return redirect("/login")
    else:
        return render_template("register.html")



@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if symbol == None:
            return apology("must provide symbol", 400)
        user_id = session["user_id"]
        shares = db.cur.execute("SELECT sum(shares) FROM transactions WHERE user_id = ? AND symbol = ?", (user_id, symbol))
        shares = shares.fetchone()
        shares = shares[0]
        input_shares = int(request.form.get("shares"))
        if shares < input_shares:
            return apology("you dont have that amount of shares", 400)
        price = lookup(symbol)
        price = price["price"]
        cash = price * input_shares
        shares = input_shares * (-1)
        time = datetime.datetime.now()
        time = time.strftime("%Y-%m-%d %H:%M:%S")
        db.cur.execute("INSERT INTO transactions (user_id, symbol, price, shares, time) VALUES (?, ?, ?, ?, ?)", (user_id, symbol, price, shares, time))
        db.con.commit()
        user_cash = db.cur.execute("SELECT cash FROM users WHERE id = ?", (user_id,))
        user_cash = user_cash.fetchone()
        cash = user_cash[0] + cash
        db.cur.execute("UPDATE users SET cash = ? WHERE id=?", (cash, user_id))
        db.con.commit()
        return redirect("/")
    else:
        user_id = session["user_id"]
        symbols = db.cur.execute("SELECT symbol FROM transactions WHERE user_id= ? GROUP BY symbol", (user_id,))
        symbols = symbols.fetchall()
        return render_template("sell.html", symbols=symbols)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
