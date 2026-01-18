import requests
import secrets
from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
# In production, this URL should be configurable via env vars
API_URL = "http://localhost:8000"

# Admin Authentication Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Admin Routes ---

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Hardcoded credentials for demo
        if username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error="Invalid credentials")
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/admin')
@login_required
def admin_dashboard():
    try:
        bookings = requests.get(f"{API_URL}/bookings/").json()
        pending_count = sum(1 for b in bookings if b.get('status') == 'pending')
        confirmed_count = sum(1 for b in bookings if b.get('status') == 'confirmed')
    except requests.exceptions.RequestException:
        bookings = []
        pending_count = 0
        confirmed_count = 0
    
    return render_template('admin_dashboard.html', 
                         bookings=bookings, 
                         title="Dashboard",
                         pending_count=pending_count,
                         confirmed_count=confirmed_count)

@app.route('/admin/bookings')
@login_required
def admin_bookings():
    try:
        bookings = requests.get(f"{API_URL}/bookings/").json()
    except requests.exceptions.RequestException:
        bookings = []
    return render_template('admin_bookings.html', bookings=bookings, title="Manage Bookings")

@app.route('/admin/booking/<int:booking_id>/update', methods=['POST'])
@login_required
def update_booking_status(booking_id):
    new_status = request.form.get('status')
    try:
        requests.put(f"{API_URL}/bookings/{booking_id}/status", json={"status": new_status})
    except requests.exceptions.RequestException:
        flash("Error updating status", "error")
    return redirect(url_for('admin_bookings'))

@app.route('/admin/destinations')
@login_required
def admin_destinations():
    try:
        destinations = requests.get(f"{API_URL}/destinations/").json()
    except requests.exceptions.RequestException:
        destinations = []
    return render_template('admin_destinations.html', destinations=destinations, title="Manage Destinations")

@app.route('/admin/destination/<int:destination_id>/delete', methods=['POST'])
@login_required
def delete_destination(destination_id):
    try:
        requests.delete(f"{API_URL}/destinations/{destination_id}")
    except requests.exceptions.RequestException:
        flash("Error deleting destination", "error")
    return redirect(url_for('admin_destinations'))

# --- Public Routes ---

@app.route('/')
def home():
    try:
        # Fetch data from FastAPI backend
        destinations = requests.get(f"{API_URL}/destinations/").json()
        packages = requests.get(f"{API_URL}/packages/").json()
    except requests.exceptions.RequestException:
        destinations = []
        packages = []
        print("Error connecting to backend API")

    # Parse features string to list for packages
    for p in packages:
        if 'features' in p and isinstance(p['features'], str):
            p['features'] = p['features'].split(',')

    return render_template('index.html', destinations=destinations, packages=packages)

@app.route('/package/<int:package_id>')
def package_details(package_id):
    try:
        response = requests.get(f"{API_URL}/packages/{package_id}")
        if response.status_code == 200:
            package = response.json()
            if package.get('features'):
                 package['features'] = package['features'].split(',')
            return render_template('details.html', package=package)
        else:
            return "Package not found", 404
    except requests.exceptions.ConnectionError:
        return "Backend not reachable", 500

if __name__ == '__main__':
    app.run(debug=True, port=6004)
