from flask import Blueprint, session, request, jsonify, make_response, render_template
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app as app


auth = Blueprint('auth', __name__)


########################################################################################### Creates JWT token ###########################################################################################
def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'Alert!': 'Token is missing!'}), 403
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'Alert!': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'Alert!': 'Invalid Token!'}), 401
        
        return func(payload=payload, *args, **kwargs)
    return decorated



###################################################################################################### (Testing)  ###########################################################################################
@auth.route('/public')
def public():
    return 'This is for the public'



########################################################################################### (Testing) Tests the authenticity of the jwt code ###########################################################################################
@token_required
def auth_route():
    return 'JWT is verified. Welcome to your dashboard!'



########################################################################################### Home route ###########################################################################################
@auth.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return 'Logged in currently'



########################################################################################### Login route ###########################################################################################
@auth.route('/login', methods=['POST'])
def login():
    if request.form['username'] == 'Ronnie' and request.form['password']:
        session['logged_in'] = True
        token = jwt.encode({
            'user': request.form['username'],
            'expiration': str(datetime.utcnow() + timedelta(seconds=120))
        }, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token})
    else:
        return make_response('Unable to verify', 403, {'WWW-Authenticate': 'Basic realm: "Authenticate Failed!"'})
