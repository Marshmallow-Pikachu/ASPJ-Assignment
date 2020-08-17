from flask import Blueprint, request, jsonify, current_app
from Database import UserSchema, User, db
import jwt
import uuid
from functools import wraps
import hashlib
import bcrypt
from werkzeug.exceptions import BadRequest



user_schema = UserSchema()  #expect 1 record back
users_schema = UserSchema(many=True) #expect multiple record back

admin_api = Blueprint('admin_api', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except jwt.DecodeError:
            return jsonify({'message' : 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

@admin_api.route('/allusersinfo', methods=['GET'])
@token_required
def checkalluserinfo(current_user):

    if not current_user.is_admin:
        return jsonify({'Message' : 'Acess Denied'})

    users_list = User.query.all()
    result = users_schema.dump(users_list)

    return jsonify(data=result)


#Full link /api/admin_functions/allusersinfo

@admin_api.route('/checkoneuserinfo/<public_id>', methods=['GET'])
@token_required
def checkoneuserinfo(current_user , public_id):
    if BadRequest:
        raise BadRequest()

    if not current_user.is_admin:
        return jsonify({'Message' : 'Acess Denied'})

    user = User.query.filter_by(public_id=public_id).first()

    if user:
        result = user_schema.dump(user)
        return jsonify(result)
    else:
        return jsonify(message="User does not exist"), 404

#Full link /api/admin_functions/checkoneuserinfo/


@admin_api.route('/createuser', methods=['POST'])
@token_required
def create_user(current_user):
    if BadRequest:
        raise BadRequest()
    if not current_user.is_admin:
        return jsonify({'Message' : 'Unauthorized to perform that function'})

    # data = request.get_json()

    # data_email = data['email']
    data_email = request.form['email']

    #Check for existing records
    hashed_email_data = hashlib.sha256(data_email.encode()).hexdigest()
    exists = db.session.query(User.id).filter_by(email=hashed_email_data).scalar()
    exists2 = db.session.query(User.id).filter_by(username=request.form['username']).scalar()

    if exists is None and exists2 is None:

        # hashed_password = generate_password_hash(request.form['password'], method='sha512')
        # hashed_security_Q = generate_password_hash(request.form['security_questions'], method='sha1') #with salt
        # hashed_security_ans = generate_password_hash(request.form['security_questions_answer'], method='sha512') #with salt
        hashed_password = bcrypt.hashpw(request.form['password'].encode(), bcrypt.gensalt(rounds=16))
        hashed_security_Q = bcrypt.hashpw(request.form['security_questions'].encode(), bcrypt.gensalt())
        hashed_security_ans = bcrypt.hashpw(request.form['security_questions_answer'].encode(), bcrypt.gensalt())

        new_user = User(public_id=str(uuid.uuid4()),
                        username=request.form['username'],
                        password=hashed_password,
                        email=hashed_email_data,
                        security_questions = hashed_security_Q,
                        security_questions_answer =hashed_security_ans,
                        is_active = True,
                        is_authenticated = False,
                        is_admin = False)

        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message' : 'New user created!'}) , 201

    else:
        return jsonify({'message' : 'Username or email exist!!'}), 409



#Full link /api/admin_functions/createuser

#username
#password
#email
#security_questions
#security_questions_answer

#Your's pet name ,  Mother's middle name, Your favourite food









@admin_api.route('/deleteuser/<public_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, public_id):
    if not current_user.is_admin:
        return jsonify({'Message' : 'Unauthorized to perform that function'})

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message' : 'No user found!'})

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message' : 'The user has been deleted!'})

#Full link /api/admin_functions/deleteuser/
