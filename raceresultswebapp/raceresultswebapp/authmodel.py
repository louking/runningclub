from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, \
     check_password_hash

app = Flask(__name__)

#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\temp\\test.db'
dbuser = 'testuser'
password = 'testuserpw'
dbserver = '127.0.0.1'
dbname = 'testdemo'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{uname}:{pw}@{server}/{dbname}'.format(uname=dbuser,pw=password,server=dbserver,dbname=dbname)

db = SQLAlchemy(app)
Table = db.Table
Column = db.Column
Integer = db.Integer
Float = db.Float
Boolean = db.Boolean
String = db.String
Sequence = db.Sequence
UniqueConstraint = db.UniqueConstraint
ForeignKey = db.ForeignKey
relationship = db.relationship
backref = db.backref

rolenames = ['admin','viewer']

#----------------------------------------------------------------------
def init_owner(owner,ownername,ownerpw):
#----------------------------------------------------------------------
    '''
    recreate user,role,userrole tables for owner
    
    owner gets all roles
    
    :param owner: email address of database owner
    :param ownername: name of owner
    :param ownerpw: initial password for owner
    :param rolenames: list of names of roles which will be allowed - owner gets all of these. default = {}
    '''.format(rolenames)

    # clear user, role, userrole tables
    tablenames = ['user','role','userrole','club']
    tables = []
    for tablename in tablenames:
        tables.append(db.metadata.tables[tablename])
    db.metadata.drop_all(db.engine, tables=tables)
    db.metadata.create_all(db.engine, tables=tables)
    
    # set up FSRC club
    ownerclub = Club('owner','owner')
    club = Club('fsrc','Frederick Steeplechaser Running Club')
    db.session.add(ownerclub)
    db.session.add(club)
    
    # set up roles for global, fsrc
    roles = []
    role = Role('owner')
    ownerclub.roles.append(role)
    roles.append(role)
    for rolename in rolenames:
        role = Role(rolename)
        club.roles.append(role)
        roles.append(role)
    
    # set up owner user, with appropriate roles
    user = User(owner,ownername,ownerpw)
    for role in roles:
        user.roles.append(role)
    db.session.add(user)
    
    db.session.commit()

########################################################################
# userrole associates user with their roles
########################################################################
userrole_table = Table('userrole',db.metadata,
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('role_id', Integer, ForeignKey('role.id')),
    UniqueConstraint('user_id', 'role_id')
    )

########################################################################
class User(db.Model):
########################################################################
    __tablename__ = 'user'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    email = Column(String(120), unique=True)
    name = Column(String(120))
    pw_hash = Column(String(80))  # finding 66 characters on a couple of tests
    active = Column(Boolean)
    authenticated = Column(Boolean)
    pwresetrequired = Column(Boolean)
    roles = relationship('Role', backref='users', secondary='userrole', cascade="all, delete")
        # many to many pattern - see http://docs.sqlalchemy.org/en/rel_0_8/orm/relationships.html

    #----------------------------------------------------------------------
    def __init__(self,email,name,password,pwresetrequired=False):
    #----------------------------------------------------------------------
        self.email = email
        self.name = name
        self.set_password(password)
        self.active = True
        self.authenticated = False      # not sure how this should be handled
        self.pwresetrequired = pwresetrequired
        
    #----------------------------------------------------------------------
    def __repr__(self):
    #----------------------------------------------------------------------
        return '<User %s %s>' % (self.email, self.name)

    #----------------------------------------------------------------------
    def set_password(self, password):
    #----------------------------------------------------------------------
        self.pw_hash = generate_password_hash(password)

    #----------------------------------------------------------------------
    def check_password(self, password):
    #----------------------------------------------------------------------
        return check_password_hash(self.pw_hash, password)
    
    ## the following methods are used by flask-login
    #----------------------------------------------------------------------
    def is_authenticated(self):
    #----------------------------------------------------------------------
        return self.authenticated
    
    #----------------------------------------------------------------------
    def is_active(self):
    #----------------------------------------------------------------------
        return self.active
    
    #----------------------------------------------------------------------
    def is_anonymous(self):
    #----------------------------------------------------------------------
        return False
    
    #----------------------------------------------------------------------
    def get_id(self):
    #----------------------------------------------------------------------
        return self.id
    
    #----------------------------------------------------------------------
    def __eq__(self,other):
    #----------------------------------------------------------------------
        if isinstance(other, User):
            return self.get_id() == other.get_id()
        return NotImplemented
    
    #----------------------------------------------------------------------
    def __ne__(self,other):
    #----------------------------------------------------------------------
        equal = self.__eq__(other)
        if equal is NotImplemented:
            return NotImplemented
        return not equal
    ## end of methods used by flask-login
    
#----------------------------------------------------------------------
def find_user(userid):
#----------------------------------------------------------------------
    '''
    find user in database
    
    :param userid: id or email address of user
    '''
    # if numeric, assume userid is id of user
    if type(userid) in [int,long]:
        return User.query.filter_by(id=userid).first()
    
    # if string assume email address
    if type(userid) in [str,unicode]:
        return User.query.filter_by(email=userid).first()
    
    # who knows what it was, but we didn't find it
    return None

########################################################################
class Role(db.Model):
########################################################################
    __tablename__ = 'role'
    id = Column(Integer, Sequence('role_id_seq'), primary_key=True)
    name = Column(String(10))
    club_id = Column(db.Integer, db.ForeignKey('club.id'))
    UniqueConstraint('name', 'club_id')

    #----------------------------------------------------------------------
    def __init__(self,name):
    #----------------------------------------------------------------------
        self.name = name
        
    #----------------------------------------------------------------------
    def __repr__(self):
    #----------------------------------------------------------------------
        return '<Role %s %s>' % (Club.query.filter_by(id=self.club_id).first().shname, self.name)

########################################################################
class Club(db.Model):
########################################################################
    __tablename__ = 'club'
    id = Column(Integer, Sequence('club_id_seq'), primary_key=True)
    shname = Column(String(10), unique=True)
    name = Column(String(40), unique=True)
    roles = relationship('Role',backref='club',cascade="all, delete")

    #----------------------------------------------------------------------
    def __init__(self,shname=None,name=None):
    #----------------------------------------------------------------------
        self.shname = shname
        self.name = name
        
    #----------------------------------------------------------------------
    def __repr__(self):
    #----------------------------------------------------------------------
        return '<Club %s %s>' % (self.shname,self.name)

