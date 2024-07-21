from flask import Blueprint
from flask import session, request, jsonify, make_response, render_template
import jwt
from datetime import datetime, timedelta
from functools import wraps


auth = Blueprint('auth',__name__)

#Token
def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):

        from app import create_app
        app = create_app()

        token = request.args.get('token')
        if not token:
            return jsonify({'Alert!':'Token is missing!'})
        try:
            payload: dict[str, any] = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'Alert!': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'Alert!': 'Invalid Token!'}), 401
        
        return func(payload=payload, *args, **kwargs)
    return decorated


#Public
@auth.route('/public')
def public():

    return 'this is for the public'


#Auth
@auth.route('/auth')
@token_required
def auth():

    return 'JWT is verified. Welcome to your dashboard!'


#Home
@auth.route('/')
def home():

    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return 'Logged in currently'
    

#Login
@auth.route('/login', methods=['POST'])
def login():

    from app import create_app
    app = create_app()

    if request.form['username'] and request.form['password'] == 'Ronnie':
        session['logged_in'] = True
        token =jwt.encode({
            'user': request.form['username'],
            'expiration': str(datetime.utcnow()+ timedelta(seconds=120))
        },
            app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token.decode('utf-8')})
    else:
        return make_response('Unable to verify', 403, {'WWW-Authenticate': 'Basic realm: "Authenticate Failed!'})