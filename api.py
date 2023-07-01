from flask import Flask,redirect, url_for, Response, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import (LoginManager,
                         login_required,
                         UserMixin,
                         login_user,
                         current_user,
                         logout_user)
import os
base = os.path.dirname(__file__)
from flask_migrate import Migrate
# = os.path.basename(__file__)
bcrypt = Bcrypt()
app = Flask(__name__, static_folder="assets/")
login_manager = LoginManager()
app.config["SECRET_KEY"] = 'development key'
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{base}/anonym.sqlite"
db = SQLAlchemy(app)
migrate = Migrate(db)
class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(512), nullable=False, unique=True)
    #sent_on = db.Column(db.Datetime, nullable=False)
    def __str__(self):
        return self.username    
from datetime import datetime
class Message(db.Model):
    __tablename__ = "message"
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.Integer, db.ForeignKey("user.id"))
    content = db.Column(db.String(512), nullable=False)
    sent_on = db.Column(db.DateTime, nullable=False, default = datetime.utcnow)
    def __str__(self):
        return f"<{self.owner}>"
    
@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = bcrypt.generate_password_hash(request.form.get("password"))
        create_user = User(username=username, password=password)
        db.session.add(create_user)
        try:
            db.session.commit()
        except:
            flash("User already exist!!!")
            return redirect("/register")
        return redirect("/")
    return render_template("login.html")

@app.route("/sucess")
def success():
    return render_template("success.html")

@app.route("/dashboard")
@login_required
def dash():
    user_hex = bytes(current_user.username, "utf8").hex()
    link = f"{request.host_url}/{user_hex}"
    rows = Message.query.all()
    return render_template("dashboard.html", enum_rows=enumerate(rows), username=current_user.username, link=link)

@app.route("/delete/<msg_id>")
@login_required
def delete(msg_id):
    row = Message.query.filter_by(id=msg_id).first()
    db.session.delete(row)
    db.session.commit()
    return

@app.route("/<secret>", methods=["POST", "GET"])
def msg(secret):
    if request.method == "POST":
        username  = bytes.fromhex(secret).decode("utf8")
        user = User.query.filter_by(username = username).first()
        if user:
            owner = user.id
            content = request.form.get("message")
            create_user = Message(owner=owner, content=content)
            db.session.add(create_user)
            db.session.commit()
            flash("Message sent. Create your own link")
            return redirect(url_for("register"))
        else:
            return redirect("/register")
    return render_template("message.html")

@app.route("/", methods=["POST", "GET"])
def login():
    match current_user.is_authenticated:
        case True:
            flash("Already loggedin")
            return redirect("/dashboard")
        case False:
            if request.method == "POST":
                username = request.form.get("username")
                password = bcrypt.generate_password_hash(request.form.get("password"))
                user = User.query.filter_by(username=username).first()
                if user:
                    login_user(user)#, remember=True)
                    #flash(f"Log in successful")
                    return redirect("dashboard")
                else:
                    flash("invalid user detail")
                    return redirect("register")
    return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    flash("Logged out successfully!!")
    return redirect("/")

@app.route("/")
@login_required
def index():
    return Response({"a":1}, status=200)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

migrate.init_app(app)
#migrate.db()
login_manager.init_app(app)
login_manager.login_view = "/"
login_manager.session_protection="strong"
login_manager.login_message="Login Successful"
login_manager.login_message_category="info"
#db.init_app(app)
with app.app_context():
    db.create_all()
 
if __name__ == "__main__":
    #db.create_all()
    app.run()
