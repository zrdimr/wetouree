import requests
import secrets
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
API_URL = "http://localhost:8000"

# --- Admin Authentication ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            session['admin_role'] = 'super_admin'
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error="Invalid credentials")
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))

# --- User Authentication (Firebase) ---
@app.route('/api/auth/login', methods=['POST'])
def user_login():
    data = request.json
    session['user_logged_in'] = True
    session['user_uid'] = data.get('uid')
    session['user_email'] = data.get('email')
    session['user_name'] = data.get('displayName')
    session['user_photo'] = data.get('photoURL')
    return jsonify({"status": "success"})

@app.route('/api/auth/logout', methods=['POST'])
def user_logout():
    session.pop('user_logged_in', None)
    session.pop('user_uid', None)
    session.pop('user_email', None)
    session.pop('user_name', None)
    session.pop('user_photo', None)
    return jsonify({"status": "success"})

@app.route('/api/auth/status')
def user_auth_status():
    return jsonify({
        "logged_in": session.get('user_logged_in', False),
        "user": {
            "uid": session.get('user_uid'),
            "email": session.get('user_email'),
            "name": session.get('user_name'),
            "photo": session.get('user_photo')
        } if session.get('user_logged_in') else None
    })

# --- Admin Dashboard ---
@app.route('/admin')
@login_required
def admin_dashboard():
    try:
        bookings = requests.get(f"{API_URL}/bookings/").json()
        destinations = requests.get(f"{API_URL}/destinations/").json()
        umkm_list = requests.get(f"{API_URL}/umkm/").json()
    except:
        bookings, destinations, umkm_list = [], [], []
    
    total_visitors = sum(d.get('current_visitors', 0) for d in destinations)
    active_bookings = sum(1 for b in bookings if b.get('status') in ['pending', 'confirmed'])
    
    return render_template('admin_dashboard.html',
        title="Dashboard",
        subtitle="Overview platform pariwisata Pulau Harapan",
        total_visitors=total_visitors,
        active_bookings=active_bookings,
        total_destinations=len(destinations),
        total_umkm=len(umkm_list),
        destinations=destinations[:4],
        recent_bookings=bookings[:5],
        top_umkm=sorted(umkm_list, key=lambda x: x.get('rating', 0), reverse=True)[:5]
    )

# --- Destinations ---
@app.route('/admin/destinations')
@login_required
def admin_destinations():
    try:
        destinations = requests.get(f"{API_URL}/destinations/").json()
        facilities = requests.get(f"{API_URL}/facilities/").json()
    except:
        destinations, facilities = [], []
    
    return render_template('admin_destinations.html',
        title="Destinasi",
        subtitle="Kelola destinasi wisata",
        destinations=destinations,
        facilities=facilities
    )

@app.route('/admin/destination/<int:destination_id>/toggle', methods=['POST'])
@login_required
def toggle_destination_status(destination_id):
    try:
        dest = requests.get(f"{API_URL}/destinations/{destination_id}").json()
        new_status = 'closed' if dest.get('status') == 'open' else 'open'
        requests.put(f"{API_URL}/destinations/{destination_id}", json={"status": new_status})
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for('admin_destinations'))

@app.route('/admin/destination/<int:destination_id>/delete', methods=['POST'])
@login_required
def delete_destination(destination_id):
    try:
        requests.delete(f"{API_URL}/destinations/{destination_id}")
    except:
        flash("Error deleting destination", "error")
    return redirect(url_for('admin_destinations'))

# --- Public Destination Detail ---
@app.route('/destination/<int:destination_id>')
def destination_detail(destination_id):
    try:
        destination = requests.get(f"{API_URL}/destinations/{destination_id}").json()
        facilities = requests.get(f"{API_URL}/facilities/destination/{destination_id}").json()
        all_destinations = requests.get(f"{API_URL}/destinations/").json()
        related = [d for d in all_destinations if d['id'] != destination_id][:3]
    except:
        destination = {}
        facilities = []
        related = []
    
    return render_template('destination_detail.html',
        destination=destination,
        facilities=facilities,
        related_destinations=related
    )

# --- Bookings ---
@app.route('/admin/bookings')
@login_required
def admin_bookings():
    try:
        bookings = requests.get(f"{API_URL}/bookings/").json()
    except:
        bookings = []
    
    confirmed = sum(1 for b in bookings if b.get('status') == 'confirmed')
    pending = sum(1 for b in bookings if b.get('status') == 'pending')
    cancelled = sum(1 for b in bookings if b.get('status') == 'cancelled')
    
    return render_template('admin_bookings.html',
        title="Tiket & Booking",
        subtitle="Kelola pemesanan tiket wisata",
        bookings=bookings,
        confirmed_count=confirmed,
        pending_count=pending,
        cancelled_count=cancelled
    )

@app.route('/admin/booking/<int:booking_id>/update', methods=['POST'])
@login_required
def update_booking_status(booking_id):
    new_status = request.form.get('status')
    try:
        requests.put(f"{API_URL}/bookings/{booking_id}/status", json={"status": new_status})
    except:
        flash("Error updating status", "error")
    return redirect(url_for('admin_bookings'))

# --- UMKM ---
@app.route('/admin/umkm')
@login_required
def admin_umkm():
    try:
        umkm_list = requests.get(f"{API_URL}/umkm/").json()
    except:
        umkm_list = []
    
    return render_template('admin_umkm.html',
        title="UMKM",
        subtitle="Kelola UMKM lokal",
        umkm_list=umkm_list
    )

# --- Analytics ---
@app.route('/admin/analytics')
@login_required
def admin_analytics():
    try:
        bookings = requests.get(f"{API_URL}/bookings/").json()
        destinations = requests.get(f"{API_URL}/destinations/").json()
    except:
        bookings, destinations = [], []
    
    total_visitors = sum(d.get('current_visitors', 0) for d in destinations)
    total_revenue = sum(b.get('total_price', 500000) for b in bookings if b.get('status') == 'confirmed')
    
    return render_template('admin_analytics.html',
        title="Analytics",
        subtitle="Insight dan statistik platform",
        total_visitors=total_visitors,
        total_revenue=total_revenue
    )

# --- User Management ---
@app.route('/admin/users')
@login_required
def admin_users():
    try:
        users = requests.get(f"{API_URL}/users/").json()
        roles = requests.get(f"{API_URL}/users/roles").json()
        stats = requests.get(f"{API_URL}/users/stats/overview").json()
    except:
        users, roles, stats = [], {}, {"total":0, "active":0, "inactive":0, "by_role":{}}
    
    return render_template('admin_users.html',
        title="Manajemen Pengguna",
        subtitle="Kelola user dan hak akses (RBAC)",
        users=users,
        roles=roles,
        stats=stats
    )

@app.route('/admin/users/create', methods=['POST'])
@login_required
def create_user():
    data = {
        "username": request.form.get('username'),
        "email": request.form.get('email'),
        "password": request.form.get('password'),
        "name": request.form.get('name'),
        "phone": request.form.get('phone'),
        "role": request.form.get('role'),
        "assigned_area": request.form.get('assigned_area'),
        "profile_image": request.form.get('profile_image')
    }
    try:
        requests.post(f"{API_URL}/users/register", json=data)
        flash("User berhasil dibuat!", "success")
    except:
        flash("Error creating user", "error")
    return redirect(url_for('admin_users'))

@app.route('/admin/users/<int:user_id>/update', methods=['POST'])
@login_required
def update_user_frontend(user_id):
    # This route handles both profile and role updates
    profile_data = {
        "name": request.form.get('name'),
        "email": request.form.get('email'),
        "phone": request.form.get('phone'),
        "profile_image": request.form.get('profile_image'),
        "password": request.form.get('password') or None
    }
    role_data = {
        "role": request.form.get('role'),
        "assigned_area": request.form.get('assigned_area')
    }
    
    try:
        # Update profile (includes password, name, phone, etc)
        requests.put(f"{API_URL}/users/{user_id}", json=profile_data)
        # Update role (includes role and assigned_area)
        requests.put(f"{API_URL}/users/{user_id}/role", json=role_data)
        flash("User berhasil diupdate!", "success")
    except:
        flash("Error updating user", "error")
    return redirect(url_for('admin_users'))

@app.route('/admin/users/<int:user_id>/toggle', methods=['POST'])
@login_required
def toggle_user_active(user_id):
    try:
        requests.put(f"{API_URL}/users/{user_id}/toggle-active")
        flash("Status user diupdate!", "success")
    except:
        flash("Error updating status", "error")
    return redirect(url_for('admin_users'))

@app.route('/api/users/<int:user_id>')
@login_required
def get_user_api(user_id):
    try:
        user = requests.get(f"{API_URL}/users/{user_id}").json()
        return jsonify(user)
    except:
        return jsonify({}), 404

# --- CMS Management ---
@app.route('/admin/cms')
@login_required
def admin_cms():
    try:
        contents = requests.get(f"{API_URL}/contents/").json()
    except:
        contents = []
    
    published = sum(1 for c in contents if c.get('is_published'))
    draft = len(contents) - published
    pages = sum(1 for c in contents if c.get('type') == 'page')
    
    return render_template('admin_cms.html',
        title="CMS Management",
        subtitle="Kelola semua konten website",
        contents=contents,
        published_count=published,
        draft_count=draft,
        page_count=pages
    )

@app.route('/admin/cms/create', methods=['POST'])
@login_required
def create_content():
    data = {
        "title": request.form.get('title'),
        "body": request.form.get('content'),
        "type": request.form.get('type'),
        "image_url": request.form.get('image_url') or None,
        "is_published": request.form.get('is_active') == 'true'
    }
    try:
        requests.post(f"{API_URL}/contents/", json=data)
        flash("Konten berhasil ditambahkan!", "success")
    except:
        flash("Error creating content", "error")
    return redirect(url_for('admin_cms'))

@app.route('/admin/cms/<int:content_id>/update', methods=['POST'])
@login_required
def update_content(content_id):
    data = {
        "title": request.form.get('title'),
        "body": request.form.get('content'),
        "type": request.form.get('type'),
        "image_url": request.form.get('image_url') or None,
        "is_published": request.form.get('is_active') == 'true'
    }
    try:
        requests.put(f"{API_URL}/contents/{content_id}", json=data)
        flash("Konten berhasil diupdate!", "success")
    except:
        flash("Error updating content", "error")
    return redirect(url_for('admin_cms'))

@app.route('/admin/cms/<int:content_id>/delete', methods=['POST'])
@login_required
def delete_content(content_id):
    try:
        requests.delete(f"{API_URL}/contents/{content_id}")
        flash("Konten berhasil dihapus!", "success")
    except:
        flash("Error deleting content", "error")
    return redirect(url_for('admin_cms'))

@app.route('/api/contents/<int:content_id>')
def get_content_api(content_id):
    try:
        content = requests.get(f"{API_URL}/contents/{content_id}").json()
        return jsonify(content)
    except:
        return jsonify({}), 404

# --- Content Management (Legacy) ---
@app.route('/admin/content')
@login_required
def admin_content():
    try:
        contents = requests.get(f"{API_URL}/contents/").json()
    except:
        contents = []
    
    return render_template('admin_content.html',
        title="Konten & Promo",
        subtitle="Kelola konten digital",
        contents=contents
    )

# --- Feedback ---
@app.route('/admin/feedback')
@login_required
def admin_feedback():
    try:
        feedback_list = requests.get(f"{API_URL}/feedback/").json()
    except:
        feedback_list = []
    
    emergency_count = sum(1 for f in feedback_list if f.get('type') == 'emergency')
    pending_count = sum(1 for f in feedback_list if f.get('status') == 'open')
    resolved_count = sum(1 for f in feedback_list if f.get('status') == 'resolved')
    
    return render_template('admin_feedback.html',
        title="Feedback",
        subtitle="Monitor laporan dan feedback pengunjung",
        feedback_list=feedback_list,
        emergency_count=emergency_count,
        pending_count=pending_count,
        resolved_count=resolved_count
    )

@app.route('/admin/feedback/<int:feedback_id>/update', methods=['POST'])
@login_required
def update_feedback_status(feedback_id):
    new_status = request.form.get('status')
    try:
        requests.put(f"{API_URL}/feedback/{feedback_id}", json={"status": new_status})
    except:
        flash("Error updating feedback", "error")
    return redirect(url_for('admin_feedback'))

# --- Emergency Page ---
@app.route('/emergency')
def emergency_page():
    return render_template('emergency.html')

# --- Events ---
@app.route('/admin/events')
@login_required
def admin_events():
    try:
        events = requests.get(f"{API_URL}/events/").json()
    except:
        events = []
    
    return render_template('admin_events.html',
        title="Event",
        subtitle="Kelola jadwal event wisata",
        events=events
    )

# --- Rentals Admin ---
@app.route('/admin/rentals')
@login_required
def admin_rentals():
    try:
        equipment_list = requests.get(f"{API_URL}/rentals/equipment").json()
        rentals = requests.get(f"{API_URL}/rentals/").json()
    except:
        equipment_list, rentals = [], []
    
    available_count = sum(1 for eq in equipment_list if eq.get('available', 0) > 0)
    rented_count = sum(1 for r in rentals if r.get('status') == 'active')
    total_revenue = sum(r.get('total_price', 0) for r in rentals if r.get('status') in ['active', 'returned'])
    
    return render_template('admin_rentals.html',
        title="Sewa Alat Camping",
        subtitle="Kelola penyewaan peralatan camping",
        equipment_list=equipment_list,
        rentals=rentals,
        available_count=available_count,
        rented_count=rented_count,
        total_revenue=total_revenue
    )

@app.route('/admin/rental/<int:rental_id>/update', methods=['POST'])
@login_required
def update_rental_status(rental_id):
    new_status = request.form.get('status')
    try:
        requests.put(f"{API_URL}/rentals/{rental_id}/status?status={new_status}")
    except:
        flash("Error updating rental", "error")
    return redirect(url_for('admin_rentals'))

# --- Public Rental Page ---
@app.route('/rental')
def rental_page():
    try:
        equipment = requests.get(f"{API_URL}/rentals/equipment/available").json()
    except:
        equipment = []
    return render_template('rental.html', equipment=equipment)

# --- Tour Guides Admin ---
@app.route('/admin/guides')
@login_required
def admin_guides():
    try:
        guides = requests.get(f"{API_URL}/guides/").json()
        bookings = requests.get(f"{API_URL}/guides/bookings/").json()
    except:
        guides, bookings = [], []
    
    available_count = sum(1 for g in guides if g.get('is_available'))
    active_bookings = sum(1 for b in bookings if b.get('status') in ['pending', 'confirmed'])
    total_revenue = sum(b.get('total_price', 0) for b in bookings if b.get('status') in ['confirmed', 'completed'])
    
    return render_template('admin_guides.html',
        title="Tour Guide",
        subtitle="Kelola pemandu wisata",
        guides=guides,
        bookings=bookings,
        available_count=available_count,
        active_bookings=active_bookings,
        total_revenue=total_revenue
    )

@app.route('/admin/guide/<int:booking_id>/update', methods=['POST'])
@login_required
def update_guide_booking_status(booking_id):
    new_status = request.form.get('status')
    try:
        requests.put(f"{API_URL}/guides/bookings/{booking_id}/status?status={new_status}")
    except:
        flash("Error updating booking", "error")
    return redirect(url_for('admin_guides'))

# --- Public Guides Page ---
@app.route('/guides')
def guides_page():
    try:
        guides = requests.get(f"{API_URL}/guides/available").json()
    except:
        guides = []
    return render_template('guides.html', guides=guides)

# --- Gate Check-in ---
@app.route('/admin/gate')
@login_required
def admin_gate():
    return render_template('admin_gate.html',
        title="Gate Check-in",
        subtitle="Scan tiket pengunjung"
    )

# --- Ticket View ---
@app.route('/ticket/<int:booking_id>')
def view_ticket(booking_id):
    try:
        booking_res = requests.get(f"{API_URL}/bookings/{booking_id}")
        ticket_res = requests.get(f"{API_URL}/tickets/booking/{booking_id}")
        
        if booking_res.status_code != 200:
            return "Booking not found", 404
        
        booking = booking_res.json()
        
        if ticket_res.status_code != 200:
            # Create ticket if not exists
            ticket_create = requests.post(f"{API_URL}/tickets/", json={"booking_id": booking_id})
            ticket = ticket_create.json()
        else:
            ticket = ticket_res.json()
        
        # Get package info
        package = None
        if booking.get('package_id'):
            pkg_res = requests.get(f"{API_URL}/packages/{booking['package_id']}")
            if pkg_res.status_code == 200:
                package = pkg_res.json()
        
        return render_template('ticket.html', booking=booking, ticket=ticket, package=package)
    except Exception as e:
        return f"Error: {str(e)}", 500

# --- Public Routes ---
@app.route('/')
def home():
    try:
        destinations = requests.get(f"{API_URL}/destinations/").json()
        packages = requests.get(f"{API_URL}/packages/").json()
        contents = requests.get(f"{API_URL}/contents/").json()
        umkm_list = requests.get(f"{API_URL}/umkm/").json()
    except:
        destinations, packages, contents, umkm_list = [], [], [], []

    for p in packages:
        if 'features' in p and isinstance(p['features'], str):
            p['features'] = p['features'].split(',')

    return render_template('index.html',
        destinations=destinations,
        packages=packages,
        contents=contents,
        umkm_list=umkm_list[:4]
    )

# --- All Destinations Page ---
@app.route('/destinations')
def all_destinations():
    try:
        destinations = requests.get(f"{API_URL}/destinations/").json()
    except:
        destinations = []
    
    return render_template('destinations.html', destinations=destinations)

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
    except:
        return "Backend not reachable", 500

@app.route('/marketplace')
def marketplace():
    try:
        umkm_list = requests.get(f"{API_URL}/umkm/").json()
    except:
        umkm_list = []
    return render_template('marketplace.html', umkm_list=umkm_list)

@app.route('/umkm/<int:umkm_id>')
def umkm_detail(umkm_id):
    try:
        umkm_res = requests.get(f"{API_URL}/umkm/{umkm_id}")
        if umkm_res.status_code != 200:
            return "UMKM not found", 404
        
        umkm = umkm_res.json()
        products = requests.get(f"{API_URL}/products/umkm/{umkm_id}").json()
        
        return render_template('umkm_detail.html', umkm=umkm, products=products)
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True, port=6004)
