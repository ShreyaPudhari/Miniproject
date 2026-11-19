
import mysql.connector


# Database Connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Dbms@123",
        database="on_road_assistance"
    )


# Test Database Connection
def test_db_connection():

    connection = None

    try:
        connection = get_db_connection()
        print("MySQL connected successfully!")

    except Exception as e:
        print("MySQL connection failed:", e)

    finally:
        if connection and connection.is_connected():
            connection.close()
