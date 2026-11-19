
from flask import Blueprint, render_template, request
from database import get_db_connection
from markupsafe import escape

customer = Blueprint("customer", __name__)


# Customer Home Page
@customer.route("/customer_home")
def customer_home():
    return render_template("customer_home.html")


# Breakdown Assistance Page
@customer.route("/breakdown")
def breakdown():
    return render_template("breakdown.html")


# Submit Breakdown Request
@customer.route("/submit_breakdown", methods=["POST"])
def submit_breakdown():

    name = request.form.get("name")
    mobile = request.form.get("mobile")
    vehicle = request.form.get("vehicle")
    problem = request.form.get("problem")
    location = request.form.get("location")

    connection = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            INSERT INTO breakdown_requests
            (name, mobile, vehicle_type, problem_description,
             current_location)
            VALUES (%s, %s, %s, %s, %s)
        """

        values = (name, mobile, vehicle, problem, location)

        cursor.execute(query, values)
        connection.commit()
        cursor.close()

        return f"""
            <h2>Breakdown Request Saved Successfully!</h2>
            <p>Thank you, {escape(name)}.</p>
            <p>Your request has been recorded.</p>
            <a href="/customer_home">Back to Customer Home</a>
        """

    except Exception as e:
        return f"Database error: {escape(str(e))}", 500

    finally:
        if connection and connection.is_connected():
            connection.close()


# Fuel Assistance Page
@customer.route("/fuel")
def fuel():
    return render_template("fuel.html")


# Submit Fuel Request
@customer.route("/submit_fuel", methods=["POST"])
def submit_fuel():

    name = request.form.get("name")
    mobile = request.form.get("mobile")
    vehicle = request.form.get("vehicle")
    fuel_type = request.form.get("fuel_type")
    quantity = request.form.get("quantity")
    location = request.form.get("location")

    connection = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            INSERT INTO fuel_requests
            (name, mobile, vehicle_type, fuel_type, quantity, location)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (
            name, mobile, vehicle, fuel_type, quantity, location
        )

        cursor.execute(query, values)
        connection.commit()
        cursor.close()

        return f"""
            <h2>Fuel Request Saved Successfully!</h2>
            <p>Thank you, {escape(name)}.</p>
            <p>Your fuel request has been recorded.</p>
            <a href="/customer_home">Back to Customer Home</a>
        """

    except Exception as e:
        return f"Database error: {escape(str(e))}", 500

    finally:
        if connection and connection.is_connected():
            connection.close()
