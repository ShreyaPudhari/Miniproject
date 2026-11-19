
from flask import Blueprint, render_template, request, redirect, url_for, session
from database import get_db_connection
from markupsafe import escape

admin = Blueprint("admin", __name__)


# Admin Login
@admin.route("/admin", methods=["GET", "POST"])
def admin_login():

    error = ""

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == "onroadadmin" and password == "onroadassistance":
            session["admin"] = username
            return redirect(url_for("admin.admin_dashboard"))
        else:
            error = "Invalid username or password!"

    return render_template("admin_login.html", error=error)


# Admin Dashboard
@admin.route("/admin_dashboard")
def admin_dashboard():

    if "admin" not in session:
        return redirect(url_for("admin.admin_login"))

    return render_template("admin_dashboard.html")


# View Breakdown Requests
@admin.route("/admin_breakdown_requests")
def admin_breakdown_requests():

    if "admin" not in session:
        return redirect(url_for("admin.admin_login"))

    connection = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, name, mobile, vehicle_type,
                   problem_description, current_location,
                   created_at, assigned_provider_id, assignment_status
            FROM breakdown_requests
            ORDER BY id DESC
        """)

        requests_data = cursor.fetchall()

        cursor.execute("""
            SELECT id, name, service_type, location
            FROM service_providers
            WHERE availability = 'Available'
            AND service_type = 'Mechanic'
        """)

        providers = cursor.fetchall()

        cursor.close()

        return render_template(
            "admin_breakdown_requests.html",
            requests=requests_data,
            providers=providers
        )

    except Exception as e:
        return f"Database error: {escape(str(e))}", 500

    finally:
        if connection and connection.is_connected():
            connection.close()


# View Fuel Requests
@admin.route("/admin_fuel_requests")
def admin_fuel_requests():

    if "admin" not in session:
        return redirect(url_for("admin.admin_login"))

    connection = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, name, mobile, vehicle_type,
                   fuel_type, quantity, location,
                   created_at, assigned_provider_id, assignment_status
            FROM fuel_requests
            ORDER BY id DESC
        """)

        requests_data = cursor.fetchall()

        cursor.execute("""
            SELECT id, name, service_type, location
            FROM service_providers
            WHERE availability = 'Available'
            AND service_type = 'Fuel Delivery'
        """)

        providers = cursor.fetchall()

        cursor.close()

        return render_template(
            "admin_fuel_requests.html",
            requests=requests_data,
            providers=providers
        )

    except Exception as e:
        return f"Database error: {escape(str(e))}", 500

    finally:
        if connection and connection.is_connected():
            connection.close()


# Manage Service Providers
@admin.route("/admin_service_providers")
def admin_service_providers():

    if "admin" not in session:
        return redirect(url_for("admin.admin_login"))

    connection = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, name, mobile, service_type,
                   location, availability
            FROM service_providers
        """)

        providers = cursor.fetchall()
        cursor.close()

        return render_template(
            "admin_service_providers.html",
            providers=providers
        )

    except Exception as e:
        return f"Database error: {escape(str(e))}", 500

    finally:
        if connection and connection.is_connected():
            connection.close()


# Update Provider Availability
@admin.route("/update_provider_availability", methods=["POST"])
def update_provider_availability():

    if "admin" not in session:
        return redirect(url_for("admin.admin_login"))

    provider_id = request.form.get("provider_id")
    availability = request.form.get("availability")

    if not provider_id or not provider_id.isdigit():
        return "Invalid provider ID", 400

    if availability not in ["Available", "Not Available"]:
        return "Invalid availability value", 400

    connection = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE service_providers
            SET availability = %s
            WHERE id = %s
        """, (availability, provider_id))

        connection.commit()
        cursor.close()

        return redirect(url_for("admin.admin_service_providers"))

    except Exception as e:
        return f"Database error: {escape(str(e))}", 500

    finally:
        if connection and connection.is_connected():
            connection.close()

# Assign Provider to Breakdown Request
@admin.route("/assign_breakdown_provider", methods=["POST"])
def assign_breakdown_provider():

    if "admin" not in session:
        return redirect(url_for("admin.admin_login"))

    request_id = request.form.get("request_id")
    provider_id = request.form.get("provider_id")

    if not request_id or not request_id.isdigit():
        return "Invalid request ID", 400

    if not provider_id or not provider_id.isdigit():
        return "Invalid provider ID", 400

    connection = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Check whether the provider is an available mechanic
        cursor.execute("""
            SELECT id FROM service_providers
            WHERE id = %s
            AND service_type = 'Mechanic'
            AND availability = 'Available'
        """, (provider_id,))

        provider = cursor.fetchone()

        if not provider:
            return "Selected mechanic is not available.", 400

        # Assign provider to breakdown request
        cursor.execute("""
            UPDATE breakdown_requests
            SET assigned_provider_id = %s,
                assignment_status = 'Assigned'
            WHERE id = %s
        """, (provider_id, request_id))

        if cursor.rowcount == 0:
            connection.rollback()
            return "Breakdown request not found.", 404

        connection.commit()

        return redirect(url_for("admin.admin_breakdown_requests"))

    except Exception as e:
        if connection:
            connection.rollback()
        return f"Database error: {escape(str(e))}", 500

    finally:
        if connection and connection.is_connected():
            connection.close()


# Assign Provider to Fuel Request
@admin.route("/assign_fuel_provider", methods=["POST"])
def assign_fuel_provider():

    if "admin" not in session:
        return redirect(url_for("admin.admin_login"))

    request_id = request.form.get("request_id")
    provider_id = request.form.get("provider_id")

    if not request_id or not request_id.isdigit():
        return "Invalid request ID", 400

    if not provider_id or not provider_id.isdigit():
        return "Invalid provider ID", 400

    connection = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Check whether the provider is an available fuel provider
        cursor.execute("""
            SELECT id FROM service_providers
            WHERE id = %s
            AND service_type = 'Fuel Delivery'
            AND availability = 'Available'
        """, (provider_id,))

        provider = cursor.fetchone()

        if not provider:
            return "Selected fuel provider is not available.", 400

        # Check whether the fuel request exists
        cursor.execute("""
            SELECT id FROM fuel_requests
            WHERE id = %s
        """, (request_id,))

        fuel_request = cursor.fetchone()

        if not fuel_request:
            return "Fuel request not found.", 404

        # Assign provider to fuel request
        cursor.execute("""
            UPDATE fuel_requests
            SET assigned_provider_id = %s,
                assignment_status = 'Assigned'
            WHERE id = %s
        """, (provider_id, request_id))

        connection.commit()
        cursor.close()

        return redirect(url_for("admin.admin_fuel_requests"))

    except Exception as e:
        if connection:
            connection.rollback()
        return f"Database error: {escape(str(e))}", 500

    finally:
        if connection and connection.is_connected():
            connection.close()

# Admin Logout
@admin.route("/admin_logout")
def admin_logout():

    session.pop("admin", None)

    return redirect(url_for("admin.admin_login"))
