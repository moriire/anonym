from flask import Flask,redirect, url_for, Response, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import (LoginManager,
                         login_required,
                         UserMixin,
                         login_user,
                         current_user,
                         logout_user)
from flask_migrate import Migrate
bcrypt = Bcrypt()
app = Flask(__name__, static_folder="assets/")
login_manager = LoginManager()
app.config["SECRET_KEY"] = 'development key'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///anonym.sqlite"
db = SQLAlchemy(app)
migrate = Migrate(db)
class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(512), nullable=False, unique=True)
    #sent_on = db.Column(db.Datetime, nullable=False)
    def __str__(self):
        return self.id
    
class Message(db.Model):
    __tablename__ = "message"
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.Integer, db.ForeignKey("user.id"))
    content = db.Column(db.String(512), nullable=False)
    #sent_on = db.Column(db.Datetime(100), nullable=False)
    def __str__(self):
        return self.owner
    
@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = bcrypt.generate_password_hash(request.form.get("password"))
        create_user = User(username=username, password=password)
        db.session.add(create_user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/sucess")
def success():
    return render_template("success.html")

@app.route("/dashboard")
@login_required
def dash():
    rows = Message.query.all()
    return render_template("dashboard.html", rows=rows)

@app.route("/secret", methods=["POST", "GET"])
def msg():
    if request.method == "POST":
        query = request.args.to_dict()
        user = query.get("user", None)
        if user:
            print(user)
            owner = user
        else:
            redirect(url_for("index"))
        content = request.form.get("message")
        create_user = Message(owner=owner, content=content)
        db.session.add(create_user)
        db.session.commit()
        return redirect(url_for("success"))
    return render_template("message.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = bcrypt.generate_password_hash(request.form.get("password"))
        user = User.query.filter_by(username=username).first()
        if user:
            login_user(user, remember=True)
            return redirect(url_for("dash"))
    return render_template("login.html", data = request.form)

@app.route("/logout")
def logout():
    if User.is_authenticated():
        logout_user()
        redirect(url_for("index"))

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
login_manager.login_view = "login"
login_manager.session_protection="strong"
login_manager.login_message="Login Successful"
login_manager.login_message_category="info"
#db.init_app(app)
with app.app_context():
    db.create_all()
 
if __name__ == "__main__":
    #db.create_all()
    app.run()