from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from auth import auth
from views import views


db = SQLAlchemy()


########################################################################################### Creates app instance ###########################################################################################
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app


########################################################################################### Creates the database instance ###########################################################################################
def create_database(app):
    with app.app_context():
        db.create_all()


if __name__ == '__main__':
    app = create_app()
    create_database(app)
    app.run(debug=True, port=5002)

