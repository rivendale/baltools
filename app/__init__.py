# To Install Sentry: pip install --upgrade 'sentry-sdk[flask]'
import sentry_sdk

from flask import Flask
from config import Config

from sentry_sdk.integrations.flask import FlaskIntegration
from flask_bootstrap import Bootstrap

# Sentry Monitoring 
sentry_sdk.init(
    dsn="https://2a6ccde7b07247b3bad2213890727eb0@o530426.ingest.sentry.io/5653967",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)

# Setup app
app = Flask(__name__)

# Enables default secret-key for use with Flask-Forms
app.config.from_object(Config)

# Using Flask-Bootstrap   
bootstrap = Bootstrap(app)

# Enables use of Routes 
from app import routes
