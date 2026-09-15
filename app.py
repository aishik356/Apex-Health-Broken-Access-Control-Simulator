from flask import Flask, request, jsonify, session, render_template_string, redirect, url_for

app = Flask(__name__)
app.secret_key = "apex_health_super_secret_key"

# In-memory database
USERS = {
    "alice": {"name": "Alice Morgan", "role": "patient", "id": 101, "dob": "1994-06-12", "blood": "O+"},
    "bob":   {"name": "Bob Vance",    "role": "patient", "id": 102, "dob": "1988-11-03", "blood": "A-"},
    "admin": {"name": "Dr. Sarah Croft (Admin)", "role": "admin", "id": 999, "dob": "1980-01-20", "blood": "B+"}
}

RECORDS = {
    101: {
        "patient_name": "Alice Morgan",
        "patient_id": 101,
        "doctor": "Dr. Miller (General Physician)",
        "diagnosis": "Acute Allergic Rhinitis",
        "prescription": "Cetirizine 10mg OD, Fluticasone Nasal Spray",
        "notes": "Patient reported seasonal symptoms. Follow up in 3 months.",
        "admission_date": "2026-02-14",
        "status": "Outpatient"
    },
    102: {
        "patient_name": "Bob Vance",
        "patient_id": 102,
        "doctor": "Dr. Mehta (Cardiology)",
        "diagnosis": "Stage 2 Essential Hypertension",
        "prescription": "Amlodipine 5mg OD, Telmisartan 40mg",
        "notes": "CONFIDENTIAL: High cardiovascular risk factor. Dietary sodium restriction advised.",
        "admission_date": "2026-01-28",
        "status": "Active Monitoring"
    }
}

ALL_USERS_DB = [
    {"id": 101, "username": "alice", "name": "Alice Morgan", "role": "patient", "status": "Active"},
    {"id": 102, "username": "bob", "name": "Bob Vance", "role": "patient", "status": "Active"},
    {"id": 103, "username": "charlie", "name": "Charlie Day", "role": "patient", "status": "Discharged"}
]

# Security state toggle
SECURE_MODE = False

# -------------------------------------------------------------
# Frontend HTML Template (Realistic Clinical UI)
# -------------------------------------------------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Apex Health Systems | Patient & Staff Portal</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #0284c7;
            --primary-dark: #0369a1;
            --surface: #ffffff;
            --bg: #f8fafc;
            --border: #e2e8f0;
            --text-dark: #0f172a;
            --text-muted: #64748b;
            --danger: #ef4444;
            --success: #10b981;
        }
        * { box-sizing: border-box; font-family: 'Inter', sans-serif; margin: 0; padding: 0; }
        body { background-color: var(--bg); color: var(--text-dark); min-height: 100vh; display: flex; flex-direction: column; }
        
        /* Navigation */
        .navbar { background: #ffffff; border-bottom: 1px solid var(--border); padding: 12px 32px; display: flex; justify-content: space-between; align-items: center; }
        .logo { display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 19px; color: var(--primary-dark); }
        .logo-icon { width: 32px; height: 32px; background: var(--primary); border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-weight: 800; font-size: 18px; }
        .nav-items { display: flex; align-items: center; gap: 18px; }
        .user-pill { background: #f1f5f9; border: 1px solid var(--border); padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 500; }
        
        /* Floating Security Switcher */
        .security-badge-banner {
            position: fixed; bottom: 20px; right: 20px; z-index: 1000;
            background: #1e293b; color: white; padding: 14px 18px; border-radius: 12px;
            box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3); display: flex; align-items: center; gap: 14px;
        }
        .sec-btn { background: #334155; color: white; border: none; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: 600; }
        .status-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
        .vuln-dot { background: var(--danger); box-shadow: 0 0 8px var(--danger); }
        .sec-dot { background: var(--success); box-shadow: 0 0 8px var(--success); }

        .container { max-width: 1100px; margin: 30px auto; padding: 0 20px; flex: 1; width: 100%; }

        /* Login Card */
        .login-wrapper { max-width: 420px; margin: 40px auto; background: white; padding: 32px; border-radius: 12px; border: 1px solid var(--border); box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
        .login-wrapper h2 { font-size: 22px; margin-bottom: 8px; }
        .login-wrapper p { color: var(--text-muted); font-size: 14px; margin-bottom: 24px; }
        .form-group { margin-bottom: 16px; }
        .form-group label { display: block; font-size: 13px; font-weight: 600; margin-bottom: 6px; }
        .form-group input { width: 100%; padding: 10px 14px; border: 1px solid var(--border); border-radius: 6px; font-size: 14px; }
        .form-group input:focus { outline: none; border-color: var(--primary); }
        .btn-primary { background: var(--primary); color: white; border: none; padding: 12px; border-radius: 6px; width: 100%; font-weight: 600; cursor: pointer; font-size: 15px; }
        .btn-primary:hover { background: var(--primary-dark); }
        .hint-box { margin-top: 20px; padding: 12px; background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 6px; font-size: 12px; color: #0369a1; }

        /* Dashboard */
        .dashboard-header { margin-bottom: 24px; }
        .dashboard-header h1 { font-size: 26px; }
        .grid-layout { display: grid; grid-template-columns: 2fr 1fr; gap: 24px; }
        .card { background: white; border: 1px solid var(--border); border-radius: 10px; padding: 24px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }
        .card-title { font-size: 17px; font-weight: 600; margin-bottom: 16px; padding-bottom: 10px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }
        
        .info-row { display: flex; margin-bottom: 12px; font-size: 14px; }
        .info-label { width: 150px; font-weight: 600; color: var(--text-muted); }
        .info-val { flex: 1; }

        .search-bar { display: flex; gap: 8px; margin-bottom: 20px; }
        .search-bar input { padding: 8px 12px; border: 1px solid var(--border); border-radius: 6px; width: 180px; }
        .btn-small { background: var(--primary); color: white; border: none; padding: 8px 14px; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500; }
        
        .alert { padding: 12px 16px; border-radius: 6px; margin-bottom: 16px; font-size: 14px; }
        .alert-error { background: #fef2f2; border: 1px solid #fecaca; color: #991b1b; }
        .alert-success { background: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; }

        /* Admin Table */
        table { width: 100%; border-collapse: collapse; font-size: 14px; margin-top: 10px; }
        th, td { text-align: left; padding: 12px; border-bottom: 1px solid var(--border); }
        th { background: #f8fafc; font-weight: 600; color: var(--text-muted); }
        .btn-danger { background: var(--danger); color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 12px; font-weight: 500; }
    </style>
</head>
<body>

    <!-- Top Navigation Bar -->
    <nav class="navbar">
        <div class="logo">
            <div class="logo-icon">+</div>
            <span>Apex Health Portal</span>
        </div>
        <div class="nav-items">
            {% if session.get('username') %}
                <div class="user-pill">
                    Authenticated: <b>{{ session.get('name') }}</b> (Role: <span style="color:var(--primary); font-weight:600;">{{ session.get('role') | upper }}</span>)
                </div>
                <a href="/portal" style="font-size:14px; color:var(--text-dark); text-decoration:none; font-weight:500;">My Records</a>
                <a href="/admin" style="font-size:14px; color:var(--text-dark); text-decoration:none; font-weight:500;">Admin Panel</a>
                <a href="/logout" class="btn-small" style="background:#64748b; text-decoration:none;">Sign Out</a>
            {% else %}
                <span style="font-size: 13px; color: var(--text-muted);">Secure Patient & Staff Gateway</span>
            {% endif %}
        </div>
    </nav>

    <!-- Lab Security Switcher (Floating Control) -->
    <div class="security-badge-banner">
        <div>
            <span class="status-dot {% if secure_mode %}sec-dot{% else %}vuln-dot{% endif %}"></span>
            <span style="font-size: 13px; margin-left: 6px;">Server Mode: <b>{% if secure_mode %}SECURE (RBAC Enforced){% else %}VULNERABLE (Broken Access Control){% endif %}</b></span>
        </div>
        <form action="/toggle_security" method="POST" style="display:inline;">
            <button class="sec-btn" type="submit">Switch Mode</button>
        </form>
    </div>

    <div class="container">

        <!-- ==================== VIEW 1: LOGIN ==================== -->
        {% if view == 'login' %}
        <div class="login-wrapper">
            <h2>Sign In</h2>
            <p>Enter your patient or medical staff credentials</p>

            {% if error %}
                <div class="alert alert-error">{{ error }}</div>
            {% endif %}

            <form action="/login" method="POST">
                <div class="form-group">
                    <label>Username / Patient ID</label>
                    <input type="text" name="username" placeholder="e.g. alice, bob, or admin" required>
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password" placeholder="Any password accepted for testing" required>
                </div>
                <button type="submit" class="btn-primary">Access Health Portal</button>
            </form>

            <div class="hint-box">
                <b>Demo Accounts Available:</b><br>
                • <b>alice</b> (Patient ID: 101)<br>
                • <b>bob</b> (Patient ID: 102)<br>
                • <b>admin</b> (System Administrator / Doctor)<br>
                <i>(Enter any password you like)</i>
            </div>
        </div>
        {% endif %}

        <!-- ==================== VIEW 2: PATIENT PORTAL ==================== -->
        {% if view == 'portal' %}
        <div class="dashboard-header">
            <h1>Clinical Health Dashboard</h1>
            <p style="color: var(--text-muted);">View diagnoses, outpatient prescriptions, and laboratory reports.</p>
        </div>

        {% if error_msg %}
            <div class="alert alert-error"><b>Access Denied:</b> {{ error_msg }}</div>
        {% endif %}

        <div class="grid-layout">
            <div>
                <!-- Medical Record Card -->
                <div class="card">
                    <div class="card-title">
                        <span>Electronic Medical Record (EMR)</span>
                        <span style="font-size: 12px; color: var(--text-muted);">Record ID: #{{ record.patient_id }}</span>
                    </div>

                    <div class="info-row">
                        <div class="info-label">Patient Name:</div>
                        <div class="info-val"><b>{{ record.patient_name }}</b></div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">Attending Doctor:</div>
                        <div class="info-val">{{ record.doctor }}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">Primary Diagnosis:</div>
                        <div class="info-val" style="color: #b91c1c; font-weight:600;">{{ record.diagnosis }}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">Prescription:</div>
                        <div class="info-val">{{ record.prescription }}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">Clinical Notes:</div>
                        <div class="info-val" style="background:#f8fafc; padding:10px; border-radius:6px; border:1px solid var(--border);">{{ record.notes }}</div>
                    </div>
                </div>

                <!-- IDOR Demonstration Panel -->
                <div class="card" style="border-left: 4px solid var(--primary);">
                    <div class="card-title">
                        <span>Lookup Another Record (IDOR Test)</span>
                    </div>
                    <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 12px;">
                        Try querying Patient Record ID <b>101</b> (Alice) or <b>102</b> (Bob):
                    </p>
                    <form action="/portal" method="GET" class="search-bar">
                        <input type="number" name="record_id" value="{{ record.patient_id }}" placeholder="Record ID">
                        <button type="submit" class="btn-small">Query Record ID</button>
                    </form>
                    <small style="color:var(--text-muted);">URL endpoint tested: <code>/portal?record_id={{ record.patient_id }}</code></small>
                </div>
            </div>

            <!-- Side Information Column -->
            <div>
                <div class="card">
                    <div class="card-title">Patient Demographics</div>
                    <div class="info-row"><div class="info-label">ID:</div><div class="info-val">{{ user_data.id }}</div></div>
                    <div class="info-row"><div class="info-label">DOB:</div><div class="info-val">{{ user_data.dob }}</div></div>
                    <div class="info-row"><div class="info-label">Blood Group:</div><div class="info-val">{{ user_data.blood }}</div></div>
                </div>

                <div class="card">
                    <div class="card-title">Direct Escalation Test</div>
                    <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 14px;">
                        Attempt to navigate directly to the privileged administrative route:
                    </p>
                    <a href="/admin" class="btn-primary" style="display:block; text-align:center; text-decoration:none; font-size:13px;">Force Navigate to /admin</a>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- ==================== VIEW 3: ADMIN MANAGEMENT ==================== -->
        {% if view == 'admin' %}
        <div class="dashboard-header">
            <h1 style="color: #b91c1c;">Hospital Staff & Database Administration</h1>
            <p style="color: var(--text-muted);">Restricted Area: User Management and Records Deletion</p>
        </div>

        {% if message %}
            <div class="alert alert-success">{{ message }}</div>
        {% endif %}
        {% if error_msg %}
            <div class="alert alert-error">{{ error_msg }}</div>
        {% endif %}

        <div class="card">
            <div class="card-title">Registered Patient Records</div>
            <table>
                <thead>
                    <tr>
                        <th>Patient ID</th>
                        <th>Full Name</th>
                        <th>Username</th>
                        <th>Role</th>
                        <th>Status</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {% for u in users_list %}
                    <tr>
                        <td>#{{ u.id }}</td>
                        <td><b>{{ u.name }}</b></td>
                        <td><code>{{ u.username }}</code></td>
                        <td>{{ u.role }}</td>
                        <td><span style="color: var(--success); font-weight:600;">{{ u.status }}</span></td>
                        <td>
                            <form action="/admin/delete_user" method="POST" style="display:inline;">
                                <input type="hidden" name="user_id" value="{{ u.id }}">
                                <button type="submit" class="btn-danger" onclick="return confirm('Confirm deletion of patient file?')">Purge File</button>
                            </form>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}

    </div>
</body>
</html>
"""

# -------------------------------------------------------------
# Application Routing Logic
# -------------------------------------------------------------

@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for("portal"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        
        # Accepts any password for demonstration ease
        if username in USERS:
            user = USERS[username]
            session["username"] = username
            session["name"] = user["name"]
            session["role"] = user["role"]
            session["user_id"] = user["id"]
            return redirect(url_for("portal"))
        else:
            return render_template_string(
                HTML_TEMPLATE, 
                view="login", 
                error="Invalid username. Please use alice, bob, or admin.", 
                secure_mode=SECURE_MODE
            )
            
    return render_template_string(HTML_TEMPLATE, view="login", secure_mode=SECURE_MODE)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/toggle_security", methods=["POST"])
def toggle_security():
    global SECURE_MODE
    SECURE_MODE = not SECURE_MODE
    # Return to the previous page
    return redirect(request.referrer or url_for("portal"))


# -------------------------------------------------------------
# HORIZONTAL ACCESS CONTROL ENDPOINT (IDOR)
# -------------------------------------------------------------
@app.route("/portal")
def portal():
    if "username" not in session:
        return redirect(url_for("login"))

    logged_user = session["username"]
    user_data = USERS[logged_user]

    # Default to user's own record ID if not provided in URL
    requested_id = request.args.get("record_id", type=int)
    if not requested_id:
        requested_id = user_data["id"]

    target_record = RECORDS.get(requested_id)
    error_msg = None

    # VULNERABLE VS SECURE EVALUATION
    if SECURE_MODE:
        # Secure Check: Is this the patient's own record OR is the user an admin?
        if target_record and (target_record["patient_id"] != user_data["id"]) and (session.get("role") != "admin"):
            error_msg = f"403 Forbidden: Ownership Validation Failed. You are logged in as {session['name']} and do not have authorization to view Record #{requested_id}."
            target_record = RECORDS[user_data["id"]]  # Fallback to self

    if not target_record:
        target_record = {
            "patient_name": "Not Found",
            "patient_id": requested_id,
            "doctor": "N/A",
            "diagnosis": "Record does not exist in database",
            "prescription": "N/A",
            "notes": "No clinical data found for this identifier."
        }

    return render_template_string(
        HTML_TEMPLATE,
        view="portal",
        record=target_record,
        user_data=user_data,
        error_msg=error_msg,
        secure_mode=SECURE_MODE
    )


# -------------------------------------------------------------
# VERTICAL ACCESS CONTROL ENDPOINTS (Privilege Escalation)
# -------------------------------------------------------------
@app.route("/admin")
def admin_panel():
    if "username" not in session:
        return redirect(url_for("login"))

    # SECURE CHECK: Enforce Role-Based Access Control (RBAC)
    if SECURE_MODE:
        if session.get("role") != "admin":
            # Access Blocked
            return render_template_string(
                HTML_TEMPLATE,
                view="portal",
                record=RECORDS.get(session["user_id"]),
                user_data=USERS[session["username"]],
                error_msg="403 Forbidden: Administrative clearance required. Regular patients cannot access /admin.",
                secure_mode=SECURE_MODE
            )

    # VULNERABLE: Displays admin panel to any logged-in patient without checking role
    return render_template_string(
        HTML_TEMPLATE,
        view="admin",
        users_list=ALL_USERS_DB,
        secure_mode=SECURE_MODE
    )


@app.route("/admin/delete_user", methods=["POST"])
def delete_patient():
    if "username" not in session:
        return redirect(url_for("login"))

    if SECURE_MODE:
        if session.get("role") != "admin":
            return render_template_string(
                HTML_TEMPLATE,
                view="portal",
                record=RECORDS.get(session["user_id"]),
                user_data=USERS[session["username"]],
                error_msg="403 Forbidden: Unauthorized administrative state modification.",
                secure_mode=SECURE_MODE
            )

    user_id = request.form.get("user_id", type=int)
    global ALL_USERS_DB
    ALL_USERS_DB = [u for u in ALL_USERS_DB if u["id"] != user_id]

    return render_template_string(
        HTML_TEMPLATE,
        view="admin",
        users_list=ALL_USERS_DB,
        message=f"CRITICAL ACTION EXECUTED: Patient File #{user_id} purged from clinical storage by '{session['username']}'.",
        secure_mode=SECURE_MODE
    )


if __name__ == "__main__":
    app.run(port=5000, debug=True)