
from flask import Flask, render_template
from database import test_db_connection

from routes.customer import customer
from routes.provider import provider
from routes.admin import admin

app = Flask(__name__)

app.secret_key = "onroadassistance"

# Register all route files
app.register_blueprint(customer)
app.register_blueprint(provider)
app.register_blueprint(admin)


# Home Page
@app.route("/")
def home():
    return render_template("home.html")


# Run Application
if __name__ == "__main__":
    test_db_connection()
    app.run(debug=True)
