from flask import Flask, request
import json
from data import db, User, Service
from exceptions import InvalidTokenError, NoTokenError, \
                       InvalidServiceError, ExpiredTokenError

db_filename = 'post.db'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % db_filename
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

SECRET = 'secret'

db.init_app(app)
with app.app_context():
    db.create_all()

"""
create Users and establish their services
update user services
delete Users
delete services
get services of a certain user
get all users with services
"""

def authiencate():
    header = request.headers.get('Authorization')
    if header is None:
        raise NoTokenError()
    header = header.replace("Bearer ", "").strip()
    user = User.query.filter_by(session = header).first()
    if user is None:
        raise InvalidTokenError()
    if not user.verify_session(header):
        raise ExpiredTokenError()
    return user


@app.route("/")
def hello():
  return "Hello World!"


@app.route("/register/", methods=['POST'])
def register():
    """
    Registers a user.
    This does not generate a session

    Parameters:
    netid: A valid netid (string of length <=7)
    name: Name (string)
    password: A valid password (string)
    avatar: An integer representing the avatar of the user, default 0

    Returns a json string
    The following is always included regardless of success of request
        success: Whether the request succeeds (True/False)
    The following is only included if the request fails:
        error: The error if the request fails
    The following is only included if the request succeeds:
        netid
        name
        avatar
        services
        tracking
        session
        expiration
        renew
    """
    data = json.loads(request.data)
    if 'netid' in data and 'password' in data and 'name' in data:
        print(data['netid'])
        if User.query.filter_by(netid = data.get('netid')).first() is not None:
            print (User.query.filter_by(netid = data.get('netid')).first())
            return json.dumps({'success': False, 'error': 'User already exists'})
        try:
            user = User(netid = data['netid'], name = data['name'], password = data['password'], avatar = data.get('avatar'), services = data.get('services'))
            print("here")
            db.session.add(user)
            print("here")
            db.session.commit()
            print("here")
            return json.dumps({'success': True, **user.serialize_data(), **user.serialize_session()})
        except InvalidServiceError:
            return json.dumps({'success': False, 'error': 'Service not provided by site'})
        #except:
            #TODO: Make more specific when error handling is implemented in data.py
            #TODO: Catch avatar out of range error
            #return json.dumps({'success': False, 'error': 'Invalid Data'})
    else:
            return json.dumps({'success': False, 'error': 'No Netid/Password/Name Field'})


@app.route("/login/", methods = ['POST'])
def login():
    data = json.loads(request.data)

    if 'netid' not in data:
        return json.dumps({'success': False, 'error': 'No Netid Field'})

    user = User.query.filter_by(netid = data.get('netid')).first()

    if user is None:
        return json.dumps({'success': False, 'error': 'Incorrect Credentials'})

    if 'password' not in data:
        return json.dumps({'success': False, 'error': 'No Password Field'})

    if not user.verify_password(data.get('password')):
        return json.dumps({'success': False, 'error': 'Incorrect Credentials'})

    return json.dumps({'success': True, 'netid': user.netid, **user.serialize_session()})

@app.route("/renew/", methods = ['POST'])
def renew():
    data = json.loads(request.data)
    if 'renew' not in data:
        return json.dumps({'success': False, 'error': 'Renew token not provided'})
    user = User.query.filter_by(renew = data['renew']).first()
    if user is None:
        return json.dumps({'success': False, 'error': 'Invalid Renew Token'})
    user.renew_session()
    db.session.commit()
    return json.dumps({'success': True, 'netid': user.netid, **user.serialize_session()})

@app.route("/secret/", methods = ['GET'])
def secret():
    try:
        user = authiencate()
    except InvalidTokenError:
        return json.dumps({'success': False, 'error': 'Invalid Authiencation Token'})
    except NoTokenError:
        return json.dumps({'success': False, 'error': 'No Authiencation Token provided'})
    except ExpiredTokenError:
        return json.dumps({'success': False, 'error': 'Authiencation Token expired'})
    return json.dumps({'success': True, 'user': str(user), 'secret': 'Peekaboo'})

@app.route("/user/<netid>/", methods = ['GET'])
def user_get(netid):
    user = User.query.filter_by(netid = netid).first()
    if user is None:
        return json.dumps({'success': False, 'error': 'user not found'})
    return json.dumps({'success': True, **user.serialize_data()})

@app.route("/user/<netid>/services/", methods = ['POST', 'DELETE'])
def user_services(netid):
    try:
        login = authiencate()
    except InvalidTokenError:
        return json.dumps({'success': False, 'error': 'Invalid Authentication Token'})
    except NoTokenError:
        return json.dumps({'success': False, 'error': 'No Authentication Token provided'})
    except ExpiredTokenError:
        return json.dumps({'success': False, 'error': 'Authentication Token expired'})
    user = User.query.filter_by(netid = netid).first()
    if user is None or login.netid != user.netid:
        return json.dumps({'success': False, 'error': 'Request not authorized, users can only edit their own profiles'})
    data = json.loads(request.data)
    if 'services' not in data:
        return json.dumps({'success': False, 'error': 'No Service Field'})
    elif request.method == 'POST':
        return user_services_post(user, data)
    elif request.method == 'DELETE':
        return user_services_del(user, data)

def user_services_post(user, data):
    try:
        for s in data['services']:
            if Service.query.filter_by(user = user.netid, service = s).first() is None:
                serv = Service(user = user.netid, service = s)
                db.session.add(serv)
    except InvalidServiceError:
        return json.dumps({'success': False, 'error': 'Service not provided by site'})
    db.session.commit()
    return json.dumps({'success': True, **user.serialize_data()})

def user_services_del(user, data):
    for s in data['services']:
        serv = Service.query.filter_by(user = user.netid, service = s).first()
        if serv is None:
            return json.dumps({'success': False, 'error': 'Service cannot be deleted because it is not provided by the user'})
        db.session.delete(serv)
    db.session.commit()
    return json.dumps({'success': True, **user.serialize_data()})

@app.route('/service/other/', methods = ['GET'])
def get_other_service():
    l = Service.query
    for s in Service.SERVICES:
        l = l.filter(Service.service != s)
    users = []
    for o in l.all():
        users.append(User.query.filter_by(netid = o.user).first().serialize_data())
    return json.dumps({
        'success': True,
        'users': users
    })



@app.route('/service/<service>/', methods = ['GET'])
def get_service(service):
    #if service not in Service.SERVICES:
    #    return json.dumps({'success': False, 'error': 'Service not provided by site'})
    servs = Service.query.filter_by(service = service).all()
    users = []
    for s in servs:
        users.append(User.query.filter_by(netid = s.user).first().serialize_data())
    return json.dumps({
        'success': True,
        'users': users
    })


"""
@app.route("/reset/", methods = ['POST'])
def reset():
    db.session.query(Service).delete()
    #db.session.query(Track).delete()
    db.session.query(User).delete()
    db.session.commit()
    return 'True'
"""
