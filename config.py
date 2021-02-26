import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
# Load .flaskenv file that has API keys and secret key
load_dotenv(os.path.join(basedir, '.env'))



class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'default-key-generated-text'
    ETHPLORERAPI = os.environ.get('ETHPLORERAPI') or 'freekey'
    WTF_CSRF_ENABLED = True
