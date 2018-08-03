import os

from flask import Flask

def create_app(test_config  =None):
    app = Flask(__name__, instance_relative_config = True)
    app.config.from_mapping(
            SECRET_KEY = 'dev',
            DATABASE = os.path.join(app.instance_path, 'advisor.sqlite'),
            )

    if test_config is None:
        app.config.from_pyfile('config.py', silent = True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/key_input')
    def key_input():
        return 'key input'

    from . import db_connector
    db_connector.init_app(app)

    from . import chars
    app.register_blueprint(chars.char_blueprint)

    from . import acc
    app.register_blueprint(acc.key_blueprint)

    return app
