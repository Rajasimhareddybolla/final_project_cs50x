from flask import Flask,render_template,redirect,request
app = Flask(__name__)

@app.route("/",methods=["GET","POST"])
def login():
  if request.method=="GET":
    return render_template("/login.html")
@app.route("/register")
def register():
  return render_template("/register.html")
