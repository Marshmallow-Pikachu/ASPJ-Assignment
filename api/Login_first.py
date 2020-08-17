from flask import Blueprint, request, jsonify, make_response, current_app
from Database import User
import datetime
import jwt
import bcrypt


login_api = Blueprint('login_api', __name__)


@login_api.route('/apilogin')
def api_login():

    auth = request.authorization

    print(auth.username)
    print(auth.password)


    if not auth or not auth.username or not auth.password:
        print("1")
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    print('hey')
    user = User.query.filter_by(username=auth.username).first()
    print('hey')
    print(user)

    if not user:
        print("2")
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    # if check_password_hash(user.password, auth.password):
    print(bcrypt.checkpw(auth.password.encode(), user.password))

    if bcrypt.checkpw(auth.password.encode(), user.password):
        print('hey?')
        token = jwt.encode({'public_id' : user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, current_app.config['SECRET_KEY'])

        return jsonify({'token' : token.decode('UTF-8')})

    return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

#Full link: /api/api_login/apilogin



