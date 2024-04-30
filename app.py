import markdown
from flask_babel import Babel
from flask import Flask, render_template
from flask_pagedown import PageDown
from werkzeug.exceptions import HTTPException

from users import users, login_manager
from models import db, minio
from threads import threads

# Create new instance of a web application
app = Flask(__name__, instance_relative_config=False)
babel = Babel(app)
# Import web application configuration options from external python file
app.config.from_pyfile('config.py')
app.register_blueprint(users)
app.register_blueprint(threads)

login_manager.init_app(app)
db.init_app(app)
minio.init_app(app)
pagedown = PageDown(app)


@app.template_filter('render_markdown')
def render_markdown(s):
    return markdown.markdown(s)


@app.get("/")
def index():
    return render_template("index.html")


@app.errorhandler(HTTPException)
def handle_error(error):
    return render_template('error.html', error=error), error.code


with app.app_context():
    db.create_all()

# Run the web server
if __name__ == '__main__':
    app.run(debug=True)
