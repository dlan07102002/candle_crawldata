from flask import Flask
from flask_cors import CORS
from .controller.recommendation_controller import recommendation_blueprint
from .controller.content_controller import content_blueprint
from .controller.collaborative_controller import collaborative_blueprint

def create_app():
    app = Flask(__name__)

    # Đăng ký CORS
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Đăng ký các blueprint
    app.register_blueprint(recommendation_blueprint, url_prefix='/api')
    app.register_blueprint(content_blueprint, url_prefix='/content')
    app.register_blueprint(collaborative_blueprint, url_prefix='/collaborative')

    return app
