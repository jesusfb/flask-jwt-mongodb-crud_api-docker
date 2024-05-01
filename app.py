from flask import Flask
from config import app_config
from app import init_app, jwt
from app.views import api_bp
from flask_swagger_ui import get_swaggerui_blueprint

def create_app(env_name):
    app = Flask(__name__)
    app.config.from_object(app_config[env_name])

    init_app(app)
    jwt.init_app(app)

    app.register_blueprint(api_bp, url_prefix='/api')

    # Swagger UI setup
    SWAGGER_URL = '/api/docs'
    API_URL = '/static/swagger.json'

    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={  
            'suwa_api': "API Documentation"
        }
    )

    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    return app

if __name__ == "__main__":
    app = create_app("development")
    app.run(host='0.0.0.0')
