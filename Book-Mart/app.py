import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup, usd
import datetime
top_10_genres = [
    "Literary Fiction",
    "Mystery",
    "Science Fiction (Sci-Fi)",
    "Fantasy",
    "Thriller",
    "Biography",
    "Self-Help",
    "Romance",
    "Historical Fiction",
    "Non-Fiction"
]

# Configure application
app = Flask(__name__)
# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
page=0
# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///bookmart.db")

user_names = db.execute("SELECT username as name from users")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response
@app.route("/show_preview",methods=["GET","POST"])
@login_required

def show_preview():
    if request.method =="GET":
        return apology("sorry error")
    image_url = request.form.get("image")
    book = db.execute("select * from books where image=?",image_url)

    gener= book[0]["gener"].split()
    return render_template("preview.html",book=book[0],gener=gener)
books_c={"Literary":[],"Mystery":[],"Science":[],"Fantasy":[],    "Thriller":[],    "Biography":[],    "Self-Help":[],
 "Romance":[],    "Historical":[],    "Non-Fiction":[]}
@app.route("/del",methods=["GET","POST"])
@login_required
def dele():
    if request.method =="GET":
        image_url=request.args.get("image")
        name = db.execute("select bookname from books where image=?",image_url)
        namee= name[0]["bookname"]
        db.execute("delete from history where user_id=? and book_name=?",session["user_id"],namee)
        return redirect("/cart")
    else:
        image_url = request.form.get("image")
        book = db.execute("delete from books where image=?",image_url)
        return redirect("/login")
    
@app.route("/Categories")
def show_catogeries():
    pres_stock = db.execute("select * from books")
    return render_template("Categories.html")
@app.route("/")
@login_required
def index():

    pres_stocks = db.execute(
        f"select bookname,price,author,image,publisher,description,gener from books ;")
    id= session["user_id"]
    user_prefered = db.execute("select preferd from users where id = ?",id)
    geners_user=user_prefered[0]["preferd"].split()
    dic ={}
    for book in pres_stocks:
        book_geners = book["gener"].split(" ")
        gener_no = 0
        for k in geners_user:
            if k in book_geners:
                gener_no+=1
        dic[book["bookname"]]=gener_no
    final_sorted = []
    sorted_dict = dict(sorted(dic.items(), key=lambda item: item[1], reverse=True))
    for bookname in sorted_dict.keys():
        for k in pres_stocks:
            if bookname == k["bookname"]:
                final_sorted.append(k)
    return render_template(
        "home.html",stocks=final_sorted)
@app.route("/addbook",methods=["GET","POST"])
@login_required
def add():
    id = session["user_id"]
    title = request.form.get("title").capitalize()
    author = request.form.get("author")
    gener = request.form.getlist("types")
    generee=""
    for gen in gener:
        generee+=gen
        generee+=" "
    price = request.form.get("price")
    img = request.form.get("url")
    discription = request.form.get("description")
    publisher = db.execute("select * from publisher where id =?",id)
    publisher=publisher[0]["username"]
    db.execute("insert into books(bookname,price,author,image,gener,publisher,description) values (?,?,?,?,?,?,?);" ,title,price,author,img,generee,publisher,discription)
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()
    page = 0
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        if request.form.get("type")=="user":
            rows = db.execute(
                "SELECT * FROM users WHERE mail = ?", request.form.get("username")
            )
            if len(rows) != 1 or not check_password_hash(
                rows[0]["hash"], request.form.get("password")
            ):
                return apology("invalid username and/or password", 301)
            # Remember which user has logged in
            
            session["user_id"] = rows[0]["id"]
            # Redirect user to home page
            return redirect("/")
                # Ensure username exists and password is correct
        else:
            rows = db.execute(
                "SELECT * FROM publisher WHERE mail = ?", request.form.get("username")
            )
            if len(rows) != 1 or not check_password_hash(
                rows[0]["hash"], request.form.get("password")
            ):
                return apology("invalid username and/or password", 301)
            # Remember which user has logged in
            
            session["user_id"] = rows[0]["id"]
            name=db.execute("select username from publisher where id=?",session["user_id"])
            books=db.execute("select * from books where publisher=?",name[0]["username"])
            return render_template("publisher.html",geners=top_10_genres,books=books)
            # Ensure username exists and password is correct
    # Ur reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")
@app.route("/cart",methods=["GET","POST"])
def add_cart():
    if request.method=="POST":
        item = request.form.get("image")
        book = db.execute("select * from books where image =?",item)[0]["bookname"]
        boo = db.execute("select book_name from history where user_id=?",session["user_id"])
        exist = False
        for bo in boo:
            if bo["book_name"]==book:
                exist = True
        if  not exist:
            db.execute("insert into history (user_id,book_name,transaction_date ) values (?,?,?);",session["user_id"],book,datetime.datetime.now())
        else:
            pass
        return redirect("/cart")
    else:
        prodouct = db.execute("select * from history where user_id =?",session["user_id"])
        books=[]
        count=0
        for prod in prodouct:

            name = prod["book_name"]
            boo =db.execute("select * from books where bookname=?",name)
            if len(boo)==0:
                pass
            else:
                books.append(boo)
                count+=1
        return render_template("cart.html",prodoucts = books)
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user_completed"""
    if request.method == "GET":
        return render_template("register.html",geners=top_10_genres)
    if request.method == "POST":
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        name = fname+" "+lname
        age = request.form.get("age")
        age=int(age)
        mail = request.form.get("mail")
        gender  = request.form.get("gender")
        prefered = request.form.getlist("types")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        gener=""
        for genr in prefered:
            gener +=" "+genr
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
        if request.form.get("type")=="user":
            db.execute(
                "INSERT INTO users(username,hash,age,mail,gender,preferd) VALUES (?,?,?,?,?,?)",
                name,
                generate_password_hash(password),
                age,
                mail,
                gender,
                gener
                )

        else:
            try:
                db.execute(
                    "INSERT INTO publisher(username,hash,age,mail) VALUES (?,?,?,?)",
                    name,
                    generate_password_hash(password),
                    age,
                    mail
                )
            except:
                return apology("email already exist")
        return redirect("/login")
    return apology("Ran into a problem ",200)
