from flask import Flask, render_template

from auth import auth, login_manager
from models import db

# Create new instance of a web application
app = Flask(__name__, instance_relative_config=False)
# Import web application configuration options from external python file
app.config.from_pyfile('config.py')
app.register_blueprint(auth)
login_manager.init_app(app)
db.init_app(app)


@app.get("/")
def index():
    return render_template("index.html")


with app.app_context():
    db.create_all()

# Run the web server
if __name__ == '__main__':
    app.run(debug=True)
