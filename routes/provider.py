
from flask import Blueprint, render_template, request, session, redirect, url_for
from database import get_db_connection
from markupsafe import escape
from werkzeug.security import generate_password_hash, check_password_hash

provider = Blueprint("provider", __name__)


# Provider Login Page
@provider.route("/provider_login")
def provider_login():
    return render_template("provider_login.html")


# Provider Registration Page
@provider.route("/register_provider", methods=["GET", "POST"])
def register_provider():

    if request.method == "POST":

        name = request.form.get("name")
        mobile = request.form.get("mobile")
        service_type = request.form.get("service_type")
        location = request.form.get("location")
        availability = request.form.get("availability")
        password = request.form.get("password")

        if not password:
            return "Please enter a password.", 400

        password_hash = generate_password_hash(password)
        connection = None

        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            query = """
                INSERT INTO service_providers
                (name, mobile, service_type, location,
                 availability, password_hash)
                VALUES (%s, %s, %s, %s, %s, %s)
            """

            values = (
                name, mobile, service_type,
                location, availability, password_hash
            )

            cursor.execute(query, values)
            connection.commit()
            cursor.close()

            return """
                <h2>Provider Registered Successfully!</h2>
                <a href="/provider_login">Provider Login</a>
                <br><br>
                <a href="/service_providers">View Providers</a>
                <br><br>
                <a href="/">Home</a>
            """

        except Exception as e:
            return f"Database error: {escape(str(e))}", 500

        finally:
            if connection and connection.is_connected():
                connection.close()

    return render_template("provider_register.html")


# Provider Login Form
@provider.route("/provider_login_form", methods=["GET", "POST"])
def provider_login_form():

    if request.method == "POST":

        mobile = request.form.get("mobile")
        password = request.form.get("password")

        connection = None

        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute(
                "SELECT id, name, password_hash FROM service_providers WHERE mobile = %s",
                (mobile,)
            )

            result = cursor.fetchone()
            cursor.close()

            if result and result[2] and password and check_password_hash(result[2], password):

                session["provider_id"] = result[0]
                session["provider_name"] = result[1]

                return redirect(url_for("provider.provider_dashboard"))

            return "Invalid mobile number or password. Please try again."

        except Exception as e:
            return f"Database error: {escape(str(e))}", 500

        finally:
            if connection and connection.is_connected():
                connection.close()

    return render_template("provider_login_form.html")


# Provider Dashboard
@provider.route("/provider_dashboard")
def provider_dashboard():

    if "provider_id" not in session:
        return redirect(url_for("provider.provider_login"))

    connection = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT name, mobile, service_type, location, availability
            FROM service_providers
            WHERE id = %s
        """, (session["provider_id"],))

        provider_details = cursor.fetchone()
        cursor.close()

        if not provider_details:
            session.pop("provider_id", None)
            session.pop("provider_name", None)
            return redirect(url_for("provider.provider_login"))

        return render_template(
            "provider_dashboard.html",
            provider_details=provider_details
        )

    except Exception as e:
        return f"Database error: {escape(str(e))}", 500

    finally:
        if connection and connection.is_connected():
            connection.close()


# View Assigned Customer Requests
@provider.route("/provider_assigned_requests")
def provider_assigned_requests():

    if "provider_id" not in session:
        return redirect(url_for("provider.provider_login"))

    connection = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT service_type
            FROM service_providers
            WHERE id = %s
        """, (session["provider_id"],))

        provider_details = cursor.fetchone()

        if not provider_details:
            session.pop("provider_id", None)
            session.pop("provider_name", None)
            cursor.close()
            return redirect(url_for("provider.provider_login"))

        service_type = provider_details[0]

        if service_type == "Mechanic":

            cursor.execute("""
                SELECT id, name, mobile, vehicle_type,
                       problem_description, current_location,
                       created_at, assignment_status
                FROM breakdown_requests
                WHERE assigned_provider_id = %s
                ORDER BY created_at DESC
            """, (session["provider_id"],))

            assigned_requests = cursor.fetchall()
            request_type = "Breakdown"

        elif service_type == "Fuel Delivery":

            cursor.execute("""
                SELECT id, name, mobile, vehicle_type,
                       fuel_type, quantity, location,
                       created_at, assignment_status
                FROM fuel_requests
                WHERE assigned_provider_id = %s
                ORDER BY created_at DESC
            """, (session["provider_id"],))

            assigned_requests = cursor.fetchall()
            request_type = "Fuel"

        else:
            assigned_requests = []
            request_type = "Other"

        cursor.close()

        return render_template(
            "provider_assigned_requests.html",
            assigned_requests=assigned_requests,
            request_type=request_type
        )

    except Exception as e:
        return f"Database error: {escape(str(e))}", 500

    finally:
        if connection and connection.is_connected():
            connection.close()


# View Service Providers
@provider.route("/service_providers")
def service_providers():

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
            "service_providers.html",
            providers=providers
        )

    except Exception as e:
        return f"Database error: {escape(str(e))}", 500

    finally:
        if connection and connection.is_connected():
            connection.close()
