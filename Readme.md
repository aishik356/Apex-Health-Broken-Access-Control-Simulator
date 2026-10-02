Apex Health: Broken Access Control Simulator

A realistic, interactive web application built with Python and Flask to demonstrate Broken Access Control (BAC) and Insecure Direct Object Reference (IDOR) vulnerabilities.

This project simulates a hospital patient portal and features a built-in "Security Toggle" that allows users to instantly switch the server between a vulnerable state and a secure, patched state to observe the differences in server-side authorization handling.

🚀 Features

Realistic UI: Clean, clinical-themed frontend to simulate a real-world healthcare application.

Horizontal Access Control (IDOR): Demonstrates how attackers can manipulate URL parameters (?record_id=) to access confidential medical records of other patients.

Vertical Access Control (Privilege Escalation): Demonstrates how standard users can force-browse to administrative endpoints (/admin) to view sensitive data and execute destructive actions (deleting users).

Interactive Security Toggle: A floating UI button that enables/disables Role-Based Access Control (RBAC) and ownership validation in real-time.

🛠️ Installation & Setup

Clone the repository:

https://github.com/aishik356/Apex-Health-Broken-Access-Control-Simulator.git
cd Apex-Health-Broken-Access-Control-Simulator


Install dependencies:
This project requires Python and Flask.

pip install Flask


Run the application:

python app.py


The application will be hosted locally at http://127.0.0.1:5000/.

🧪 Vulnerability Walkthrough (How to Test)

1. Insecure Direct Object Reference (IDOR)

Action: Log in as alice (password doesn't matter).

Vulnerability: You will see Alice's medical record (ID: 101). In the "Lookup Another Record" box, type 102 (Bob's ID) and submit.

Result (Vulnerable): You successfully view Bob's confidential cardiology report.

The Fix: Click the "Switch Mode" button to enable Secure Mode. Try to query 102 again. You will now receive a 403 Forbidden error because the server verifies record ownership.

2. Vertical Privilege Escalation

Action: While logged in as alice (a standard patient), click the "Force Navigate to /admin" button, or manually type /admin into the URL.

Result (Vulnerable): You are granted access to the Hospital Staff Administration panel and can purge (delete) users from the database.

The Fix: Enable Secure Mode and try to access /admin again. You will be blocked by Role-Based Access Control (RBAC) verifying your session role.

🛡️ Security Concepts Demonstrated

Authentication vs. Authorization: The app demonstrates that verifying who a user is (Authentication/Login) is not enough. The server must also verify what they are allowed to do (Authorization).

Session Management: Utilizing server-side sessions to store unmodifiable user roles.

RBAC (Role-Based Access Control): Enforcing strict role checks on sensitive administrative routes.

👨‍💻 Author

Aishik Mitra
Digital Forensics & Cybersecurity Student | LinkedIn
