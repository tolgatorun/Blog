import os

from flask import Flask
#A Flask application is an instance of Flask class.Creating a global Flask instance could be tricky
#Creating inside a function known as application factory.Eveything will happen here then returned.
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)#creating Flask instance|(name of current module,config f's relative to instance folder)
    app.config.from_mapping(
        SECRET_KEY='dev',#key for safety
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),#path of db
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)#ensure app.instance_path exists
    except OSError:
        pass

    @app.route('/hello')#creates a simple route
    def hello():
        return 'Hello, World!'

    from . import db
    db.init_app(app)
    return app