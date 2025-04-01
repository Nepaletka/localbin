import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor
import ipaddress
from functools import wraps
from flask import Flask, render_template, request, redirect, session, url_for, jsonify, flash, get_flashed_messages
import check_user
import sender

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

app = Flask(__name__)
# Load secret key from environment variable for security
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key')

# Configure HOSTS from environment variable or configuration file path
HOSTS = []

def load_users():
    """Load the list of users from the users.json file."""
    try:
        with open('users.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("File users.json not found")
        return {}
    except json.JSONDecodeError:
        logging.error("Error decoding JSON in users.json")
        return {}
    except Exception as e:
        logging.error("Unknown error loading users: %s", e)
        return {}

def load_hosts():
    """Load the list of hosts from the hosts.json file."""
    global HOSTS
    try:
        with open('hosts.json', 'r', encoding='utf-8') as f:
            hosts_config = json.load(f)
            network = hosts_config.get("address")
            if not network:
                raise ValueError("Missing 'address' key in hosts.json")
            HOSTS = [str(ip) for ip in ipaddress.IPv4Network(network)]
    except FileNotFoundError:
        logging.error("File hosts.json not found. Please provide a valid hosts configuration.")
    except (json.JSONDecodeError, ValueError) as e:
        logging.error("Error processing hosts.json: %s", e)
    except Exception as e:
        logging.error("Unknown error loading hosts: %s", e)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def root():
    """Redirect to profile if logged in, otherwise to login."""
    if 'username' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('profile'))

@app.route('/profile')
def profile():
    """Display profile page with messages if logged in, otherwise redirect to login."""
    if 'username' not in session:
        return redirect(url_for('login'))
    messages = get_flashed_messages(with_categories=True)
    return render_template('profile.html', title='Профиль', username=session['username'], messages=messages)

@app.route('/logout')
def logout():
    """Handle user logout."""
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route("/login", methods=['GET', 'POST'])
def login():
    """Handle user login with GET (show form) and POST (process login)."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        users = load_users()
        if not users:
            return render_template('login.html', title='Sign In', error="Ошибка загрузки данных пользователей.")
        
        if username in users and users[username].get('password') == password:
            session['username'] = username
            logging.info("User '%s' logged in successfully.", username)
            return redirect(url_for('profile'))
        else:
            error = "Неверное имя пользователя или пароль."
            logging.warning("Login failed for user: %s", username)
            return render_template('login.html', title='Sign In', error=error)
    
    return render_template('login.html', title='Sign In')

def get_ready_hosts():
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(check_user.main, HOSTS))
    ready_hosts = [host for host in results if host is not None]
    return ready_hosts

@app.route("/api/v1/get_users", methods=['GET'])
@login_required
def api_get_users():
    """Return a JSON list of ready hosts."""
    ready_hosts = get_ready_hosts()
    return jsonify(ready_hosts), 200

@app.route("/api/v1/send_clipboard", methods=['POST'])
@login_required
def api_send_clipboard():
    """Send clipboard data to all ready hosts and redirect to profile with a message."""
    selected_computers = request.form.getlist('computers')
    clip = request.form.get('text', '')
    logging.info("Selected computers: %s", selected_computers)

    if not clip:
        flash("Нет текста для отправки", "error")
        return redirect(url_for('profile'))

    if not selected_computers:
        flash("Нет выбранных компьютеров для отправки", "error")
        return redirect(url_for('profile'))

    ready_hosts = get_ready_hosts()
    for host in ready_hosts:
        if host in selected_computers:
            if sender.send_clipboard_to_user(host, clip):
                logging.info("Clipboard sent to %s successfully", host)
            else:
                logging.error("Failed to send clipboard to %s", host)
                flash(f"Не удалось отправить буфер обмена на {host}", "error")

    flash("Буфер обмена успешно отправлен на все готовые хосты", "success")
    return redirect(url_for('profile'))

@app.route("/api/v1/get")
@login_required
def hello2_world():
    """Placeholder endpoint."""
    return "<p>Hello, World!</p>"

@app.route("/api/v1/add_user", methods=['GET'])
@login_required
def hello3_world():
    """Placeholder endpoint."""
    return "<p>Hello, World!</p>"

@app.route("/api/v1/remove_user", methods=['GET'])
@login_required
def hello4_world():
    """Placeholder endpoint."""
    return "<p>Hello, World!</p>"

if __name__ == '__main__':
    load_hosts()
    # Для продакшена используйте WSGI-сервер (например, gunicorn)
    app.run(host='0.0.0.0', port=5000)
