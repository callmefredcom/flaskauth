from flask import Flask, render_template, request, redirect, url_for, flash, g, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask_login import current_user
from dotenv import load_dotenv
import mysql.connector
import os
from itsdangerous import URLSafeTimedSerializer
from emails import send_mail_pw_reset, send_welcome_email, send_mail_verification
from functools import wraps
from flask_dance.contrib.google import make_google_blueprint, google

app = Flask(__name__)

load_dotenv()

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get('SECURITY_PASSWORD_SALT')
app.config['PREFERRED_URL_SCHEME'] = 'https'

google_bp = make_google_blueprint(
    client_id=os.environ.get('GOOGLE_OAUTH_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET'),
    scope=["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"],
    redirect_to="google_login"
)
app.register_blueprint(google_bp, url_prefix="/login")

login_manager = LoginManager()
login_manager.init_app(app)

db_password = os.environ.get('MYSQL_PASSWORD')

# MySQL configuration
DATABASE_URL = f"mysql -roundhouse.proxy.rlwy.net -uroot -p{db_password} --port 35112 --protocol=TCP railway"

DATABASE_CONFIG = {
            'user': 'root',
            'password': os.environ.get('MYSQL_PASSWORD'),
            'host': 'roundhouse.proxy.rlwy.net',
            'port': '35112',
            'database': 'railway'
        }

def get_db():
    if hasattr(g, 'db_conn') and g.db_conn.is_connected():
        return g.db_conn
    else:
        g.db_conn = mysql.connector.connect(**DATABASE_CONFIG)
        return g.db_conn

@app.teardown_appcontext
def close_db_connection(exception):
    db = getattr(g, 'db_conn', None)
    if db is not None:
        db.close()

@login_manager.unauthorized_handler
def unauthorized():
    # Redirect unauthorized users to the index page
    flash("You must be logged in to access this page.", "warning")
    return redirect(url_for('login', next=request.url))

def require_permission(feature_id):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            conn = get_db()
            cursor = conn.cursor()

            cursor.execute(
                'SELECT rf.feature_id FROM role_features rf '
                'JOIN users u ON u.role_id = rf.role_id '
                'WHERE u.id = %s AND rf.feature_id = %s',
                (current_user.id, feature_id)
            )

            result = cursor.fetchone()

            if not result:
                flash('You do not have permission to access this page.')
                return redirect(url_for('index'))
            return f(*args, **kwargs)

        return decorated_function

    return decorator


@login_manager.user_loader
def load_user(user_id):
    conn = get_db()
    cursor = conn.cursor()

    # Query to find user by the auto-incremented id
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    cursor.close()

    if user:
        user_obj = UserMixin()
        user_obj.id = user[0]  # The auto-incremented ID
        user_obj.username = user[1]
        user_obj.email = user[2]
        user_obj.password = user[3]
        user_obj.role_id = user[4]
        user_obj.email_confirmed = user[5]
        return user_obj

    return None

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = generate_password_hash(request.form.get('password'))

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE email=%s OR username=%s', (email, username))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Email or username already exists. Choose another one.')
            return redirect(url_for('signup'))

        # welcome credits logic, add 2 credits instead of O
        cursor.execute('INSERT INTO users (username, email, password, role_id) VALUES (%s, %s, %s, %s)',
                       (username, email, password, 2))

        conn.commit()
        conn.close()

        # Send email verification
        s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        token = s.dumps(email, salt='email-confirm')
        verification_url = url_for("confirm_email", token=token, _external=True)

        send_mail_verification(email, verification_url)

        session['email'] = email

        return redirect(url_for('check_email'))

    return render_template('signup.html')

@app.route('/check-email')
def check_email():
    email = session.get('email', None)
    if not email:
        return redirect(url_for('signup'))  # Or handle this case as you see fit
    return render_template('check_email.html', email=email)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE email=%s', (email,))
        user = cursor.fetchone()
        conn.close()

        # Check if user exists and password is correct
        if user and check_password_hash(user[3], password):

            # Check if the email is confirmed, assuming email_confirmed is the 7th column (index 6)
            if not user[5]:  # Adjust the index if necessary
                flash('Please verify your email before logging in. Check your inbox.')
                return redirect(url_for('login'))

            user_obj = UserMixin()
            user_obj.id = user[0]
            login_user(user_obj)
            next_page = request.form.get('next')

            print(f"Next Page: {next_page}")

            return redirect(next_page or url_for('app_page'))

        else:
            flash('Invalid email or password.')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('app_page'))
    return render_template('index.html')


@app.route('/admin', methods=['GET'])
@login_required
@require_permission(2)
def admin_dashboard():
    if current_user.role_id != 1:
        flash('Unauthorized access')
        return redirect('/')
    return render_template('admin.html')

def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])

def verify_reset_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=expiration)
    except:
        return False
    return email

@app.route('/request-reset', methods=['GET', 'POST'])
def request_reset():
    if request.method == 'POST':
        email = request.form.get('email')
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()

        if user:
            token = generate_reset_token(email)
            reset_url = url_for('reset_with_token', token=token, _external=True)

            # Use your SendInBlue function to send email with reset_url.
            send_mail_pw_reset(email,reset_url)

            flash('Password reset link has been sent to your email', 'success')
        else:
            flash('This email is not registered', 'error')
    return render_template('request_reset.html')


@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()

    # Check if the user exists in the database using their email
    cursor.execute('SELECT * FROM users WHERE email=%s', (email,))
    user = cursor.fetchone()

    if user:
        # Check if email is already confirmed
        if user[5]:
            flash('Email already confirmed. Please log in.', 'info')
            conn.close()
            return redirect(url_for('login'))

        # Update the user's email confirmation status in the database
        cursor.execute('UPDATE users SET email_confirmed = TRUE, email_confirmed_on = NOW() WHERE email = %s', (email,))
        conn.commit()

        # Send welcome email after successful email confirmation
        send_welcome_email(email)
        print("Welcome Email sent")


        flash('Thank you for confirming your email! Please log in.', 'success')

        session['email_confirmed'] = True

    else:
        flash('Error! User not found.', 'danger')

    conn.close()

    return redirect(url_for('login'))

@app.route('/resend-verification', methods=['GET', 'POST'])
def resend_verification():
    if request.method == 'POST':
        email = request.form.get('email')

        # Check if the user exists and hasn't confirmed their email
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email=%s', (email,))
        user = cursor.fetchone()
        conn.close()

        if user:
            # Generate a verification token and send the email
            s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
            token = s.dumps(email, salt='email-confirm')
            verification_url = url_for("confirm_email", token=token, _external=True)
            send_mail_verification(email, verification_url)

            flash('Verification email has been resent. Please check your inbox.', 'success')
        else:
            flash('This email address is not registered or has already been verified.', 'danger')

        return redirect(url_for('login'))

    return render_template('resend_verification.html')


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


@app.route('/static/admin.js')
@login_required
@require_permission(2)
def custom_static_admin_js():
    return send_from_directory(app.static_folder, "admin.js")

@app.route('/static/admin.css')
@login_required
@require_permission(2)
def custom_static_admin_css():
    return send_from_directory(app.static_folder, "admin.css")


@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_with_token(token):
    email = verify_reset_token(token)
    if not email:
        flash('Invalid or expired token', 'error')
        return redirect(url_for('request_reset'))

    if request.method == 'POST':
        new_password = generate_password_hash(request.form.get('password'))

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('UPDATE users SET password = %s WHERE email = %s', (new_password, email))
        conn.commit()

        flash('Password has been updated', 'success')
        return redirect(url_for('login'))
    return render_template('reset_password.html')


@app.route('/app')
@login_required
def app_page():
    return render_template('app.html')


@app.route('/google_login')
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    if resp.ok:
        google_info = resp.json()
        google_user_id = str(google_info["id"])

        # Establish a database connection
        conn = get_db()
        cursor = conn.cursor()

        # Check if the user exists in your database by their Google ID
        cursor.execute('SELECT * FROM users WHERE google_id = %s', (google_user_id,))
        user = cursor.fetchone()

        if not user:
            # User does not exist, create a new user with Google info
            username = google_info.get("name")
            email = google_info.get("email")

            # Insert new user into your database
            cursor.execute('INSERT INTO users (username, email, google_id, role_id) VALUES (%s, %s, %s, %s)',
                           (username, email, google_user_id,2))
            conn.commit()
            user_id = cursor.lastrowid  # Get the auto-incremented ID of the new user
        else:
            # User exists, get their auto-incremented ID
            user_id = user[0]

        conn.close()

        # Load the user and log them in using Flask-Login
        user_obj = load_user(user_id)
        if user_obj:
            login_user(user_obj)

        return redirect(url_for('app_page'))  # Redirect to the application's main page
    else:
        return "Failed to fetch user info from Google.", 403



@app.route('/logout/google')
def google_logout():
    token = blueprint.token["access_token"]
    resp = google.post(
        "https://accounts.google.com/o/oauth2/revoke",
        params={"token": token},
        headers={"content-type": "application/x-www-form-urlencoded"}
    )
    assert resp.ok, resp.text
    logout_user()  # Flask-Login's logout
    return redirect(url_for('index'))

@app.route('/clear-session')
def clear_session():
    session.clear()
    return 'Session cleared!'

if __name__ == '__main__':
    app.run(ssl_context=('cert.pem', 'key.pem'))