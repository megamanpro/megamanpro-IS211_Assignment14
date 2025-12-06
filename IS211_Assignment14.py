import os
import sqlite3
from datetime import datetime
from flask import Flask, g, render_template, request, redirect, url_for, session, flash


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret')
app.config['DATABASE'] = os.path.join(app.root_path, 'blog.db')

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS posts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      content TEXT NOT NULL,
      published_at TEXT NOT NULL,
      author_id INTEGER NOT NULL,
      FOREIGN KEY (author_id) REFERENCES users (id)
    );
    """)

    cur = db.execute("SELECT id FROM users WHERE username = ?", ("demo",))
    if cur.fetchone() is None:
        db.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("demo", "demo123"))
    db.commit()

@app.before_request
def setup():
    init_db()


def current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    db = get_db()
    user = db.execute("SELECT id, username FROM users WHERE id = ?", (uid,)).fetchone()
    return user

def login_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user():
            flash("Please log in to access the dashboard.", "warning")
            return redirect(url_for('login'))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/")
def index():
    db = get_db()
    posts = db.execute("""
        SELECT p.id, p.title, p.content, p.published_at, u.username AS author
        FROM posts p
        JOIN users u ON u.id = p.author_id
        ORDER BY datetime(p.published_at) DESC
    """).fetchall()
    return render_template("index.html", posts=posts, user=current_user())

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        db = get_db()
        user = db.execute("SELECT id, username, password FROM users WHERE username = ?", (username,)).fetchone()
        if user and password == user["password"]:
            session["user_id"] = user["id"]
            flash("Logged in successfully.", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid credentials.", "danger")
    return render_template("login.html", user=current_user())

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    db = get_db()
    posts = db.execute("""
        SELECT id, title, published_at
        FROM posts
        WHERE author_id = ?
        ORDER BY datetime(published_at) DESC
    """, (user["id"],)).fetchall()
    return render_template("dashboard.html", posts=posts, user=user)

@app.route("/posts/new", methods=["GET", "POST"])
@login_required
def new_post():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        if not title or not content:
            flash("Title and content are required.", "warning")
            return redirect(url_for("new_post"))
        db = get_db()
        db.execute("""
            INSERT INTO posts (title, content, published_at, author_id)
            VALUES (?, ?, ?, ?)
        """, (title, content, datetime.utcnow().isoformat(), current_user()["id"]))
        db.commit()
        flash("Post created.", "success")
        return redirect(url_for("dashboard"))
    return render_template("new_post.html", user=current_user())

@app.route("/posts/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    db = get_db()
    post = db.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    if not post or post["author_id"] != current_user()["id"]:
        flash("Post not found or access denied.", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        if not title or not content:
            flash("Title and content are required.", "warning")
            return redirect(url_for("edit_post", post_id=post_id))
        db.execute("""
            UPDATE posts SET title = ?, content = ? WHERE id = ?
        """, (title, content, post_id))
        db.commit()
        flash("Post updated.", "success")
        return redirect(url_for("dashboard"))

    return render_template("edit_post.html", post=post, user=current_user())

@app.route("/posts/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    db = get_db()
    post = db.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    if not post or post["author_id"] != current_user()["id"]:
        flash("Post not found or access denied.", "danger")
        return redirect(url_for("dashboard"))
    db.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    db.commit()
    flash("Post deleted.", "info")
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(debug=True)
