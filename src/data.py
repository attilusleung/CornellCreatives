from flask_sqlalchemy import SQLAlchemy
import datetime
from secrets import token_hex
from bcrypt import checkpw, hashpw, gensalt
from exceptions import *


db = SQLAlchemy()

#TODO: REPLACE kwargs.get with kwags[<something>] for initializers
#that need to throw an error

class User(db.Model):
    """
    A model that describes users registered in the app .

    Users are identified through their netid.
    Users are able to both provide services (services column) and seek services
    (tracking column)
    """
    netid = db.Column(db.String(7), primary_key = True)
    name = db.Column(db.String, nullable = False)
    #password
    avatar = db.Column(db.Integer, nullable = False, default = 0) #TODO: MAKE IT LINK TO A FILE
    services = db.relationship('Service', cascade = 'delete')
    #tracking = db.relationship('Track', cascade = 'delete') #check this

    #verified = db.Column(db.Boolean, nullable = False, default = False)
    password = db.Column(db.String, nullable = False)
    session = db.Column(db.String, unique = True)
    expiration = db.Column(db.DateTime)
    renew = db.Column(db.String, unique = True)


    def password_hash(self, value):
        self.password = hashpw(value.encode("utf8"), gensalt())


    def __init__(self, **kwargs):
        #asserts?
        self.netid = kwargs['netid']
        self.name = kwargs['name']
        self.avatar = kwargs.get('avatar', 0)
        #TODO: Throw an error when no such avatar is provided
        self.password_hash(kwargs['password'])

        print("here")
        if kwargs.get('services') is not None:
            for s in kwargs.get('services', []):
                print(s)
                service = Service(user = self.netid, service = s)
                db.session.add(service)

        #for t in kwargs.get('tracking', ()):
        #    track = Track(tracker = self.netid, tracking = t)
        #    db.session.add()

        #TODO: Don't autogenerate session, but verify netid is valid first (through email)
        print('here')
        self.renew_session()
        print("here")


    def generate_verification_link(self):
        #TODO: Verify netid before registering
        pass

    def renew_session(self):
        while(True):
            sessiontok = token_hex(64)
            renewtok = token_hex(64)
            if User.query.filter_by(session = sessiontok).first() is None and \
            User.query.filter_by(renew = renewtok).first() is None:
                self.session = sessiontok
                self.expiration = datetime.datetime.now() + datetime.timedelta(seconds = 3600)
                self.renew = renewtok
                break
                #print("where break?")


    def verify_password(self, password):
        return checkpw(password.encode('utf8'), self.password)


    def verify_session(self, session):
        #Check session token is redundent? You get the user by filtering by session token anyways
        return session == self.session and datetime.datetime.now() < self.expiration


    def verify_renew(self, renew): #why verify when u can just renew?
        return renew == self.renew


    def serialize_data(self):
        #TODO: INCOMPLETE
        services = []
        tracking = []
        for s in Service.query.filter_by(user = self.netid):
            services.append(str(s))
        #for t in Track.query.filter_by(tracker = self.netid):
        #    tracking.append(str(t))
        return {
            'netid': self.netid,
            'name': self.name,
            'avatar': self.avatar,
            'services': services
            #'tracking': tracking
        }


    def serialize_session(self):
        return {
            'session': self.session,
            'expiration': str(self.expiration),
            'renew': self.renew
        }


    def __str__(self):
        return self.netid



class Service(db.Model):
    #TODO: Foreign Key Error Handling? Do we need this? All services are initialized in user init block anyways
    #TODO: UPDATe SERVICES
    SERVICES = ['tutor', 'photographer', 'programmer'] #Put all services here
    id = db.Column(db.Integer, primary_key = True)
    user = db.Column(db.String(7), db.ForeignKey('user.netid'), nullable = False)
    service = db.Column(db.String(80), nullable = False)


    def __init__(self, **kwargs):
        #Call this in a try except block
        if kwargs.get('service') not in Service.SERVICES:
            raise InvalidServiceError()

        self.user = kwargs.get('user')
        self.service = kwargs.get('service')


    def serialize(self):
        return {
            'user': self.user,
            'service': self.service
        }


    def __str__(self):
        return self.service

#TODO: TRACKING
"""
class Track(db.Model):
    #TODO: Foreign Key Error Handling

    id = db.Column(db.Integer, primary_key = True)
    trackerid = db.Column(db.String(7), db.ForeignKey('user.netid'), nullable = False)
    trackingid = db.Column(db.String(7), db.ForeignKey('user.netid'), nullable = False)
    #tracker = db.relationship("User", foreign_keys = "Track.tracker")
    #tracking = db.relationship("User", foreign_keys = "Track.tracking")


    def __init__(self, **kwargs):
        self.trackerid = kwargs.get('tracker')
        self.trackingid = kwargs.get('tracking')


    def serialize(self):
        return {
            'tracker': self.tracker,
            'tracking': self.tracking
        }


    def __str__(self):
        return self.tracking
"""
