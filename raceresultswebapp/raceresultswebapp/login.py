###########################################################################################
# raceresultswebapp.login - log in / out views for race results web application
#
#       Date            Author          Reason
#       ----            ------          ------
#       10/11/13        Lou King        Create
#
#   Copyright 2013 Lou King
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
###########################################################################################

# standard
from collections import namedtuple
from functools import partial

# pypi
import flask
import flask.ext.login as flasklogin
import flask.ext.principal as principal
import flask.ext.wtf as flaskwtf
import wtforms

# home grown
from raceresultswebapp import app, authmodel
from authmodel import User,Club

login_manager = flasklogin.LoginManager(app)

#----------------------------------------------------------------------
def getnavigation():
#----------------------------------------------------------------------
    '''
    retrieve navigation list, based on current club and user's roles
    
    :param rolenames: list of role names
    :rettype: list of dicts {'display':navdisplay,'url':navurl}
    '''
    thisuser = flasklogin.current_user
    
    club = None
    if hasattr(flask.session,'club_id'):
        club = Club.query.filter_by(id=flask.session.club_id).first()
        
    navigation = []
    
    navigation.append({'display':'Home','url':flask.url_for('index')})
    
    if thisuser.is_authenticated():
        rolenames = ['owner','admin','viewer']
        if 'owner' in rolenames:
            navigation.append({'display':'Manage Clubs','url':flask.url_for('manageclubs')})
            navigation.append({'display':'Manage Users','url':flask.url_for('manageusers')})
        
    return navigation

#----------------------------------------------------------------------
def _getuserclubs(user):
#----------------------------------------------------------------------
    '''
    get clubs user has permissions for
    
    :param user: User record
    :rtype: [(club.id,club.name),...], not including 'owner' club, for select, sorted by club.name
    '''
    clubs = []
    for role in user.roles:
        thisclub = Club.query.filter_by(id=role.club_id).first()
        if thisclub.name == 'owner': continue
        clubselect = (thisclub.id,thisclub.name)
        if clubselect not in clubs:
            clubs.append(clubselect)
    decclubs = [(club[1],club) for club in clubs]
    decclubs.sort()
    return [club[1] for club in decclubs]

#----------------------------------------------------------------------
def setnavigation():
#----------------------------------------------------------------------
    '''
    set navigation based on user, club
    '''
    thisuser = flasklogin.current_user

    club = None
    if hasattr(flask.session,'club'):
        club = flask.session.club
        
    # get navigation list
    # TODO: get actual data from user's roles
    flask.session['nav'] = getnavigation()

########################################################################
########################################################################
#----------------------------------------------------------------------
@login_manager.user_loader
def load_user(userid):
#----------------------------------------------------------------------
    '''
    required by flask-login
    
    :param userid: email address of user
    '''
    # Return an instance of the User model
    user = authmodel.find_user(userid)
    if hasattr(user,'email'):
        login_manager.login_message = '{}: logged in'.format(user.email)
    return user

########################################################################
class LoginForm(flaskwtf.Form):
########################################################################
    email = wtforms.StringField()
    password = wtforms.PasswordField()

#----------------------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
#----------------------------------------------------------------------
    # define form
    form = LoginForm()

    # Validate form input for POST
    if flask.request.method == "POST" and form.validate_on_submit():
        # Retrieve the user from the datastore
        user = authmodel.find_user(form.email.data)

        # flag user doesn't exist or incorrect password
        if not (user and user.check_password(form.password.data)):
            return flask.render_template('login.html', form=form, error='username or password invalid')

        # we're good
        else:
            # Keep the user info in the session using Flask-Login
            flasklogin.login_user(user)
            user.authenticated = True   # else @login_required will fail
            flask.session['logged_in'] = True
            flask.session['user_name'] = user.name

            # Tell Flask-Principal the identity changed
            principal.identity_changed.send(
                flask.current_app._get_current_object(),
                identity=principal.Identity(user.id))
            
            userclubs = _getuserclubs(user)
            
            # zero clubs is an internal error in the databse
            if not(userclubs):
                abort(500)  # Internal Server Error
                
            # if the user only has access to one club, we're done
            if len(userclubs) == 1:
                club = Club.query.filter_by(id=userclubs[0][0]).first()
                flask.session['club_id'] = club.id
                flask.session['club_name'] = club.name
                return flask.redirect(flask.request.args.get('next') or flask.url_for('ownerconsole'))
            
            # otherwise, get the club from the user
            else:
                return flask.redirect('setclub')
            
    return flask.render_template('login.html', form=form)

########################################################################
########################################################################
#----------------------------------------------------------------------
def set_logged_out():
#----------------------------------------------------------------------
    flasklogin.logout_user()
    for key in ('logged_in','user_name','club_id','club_name'):
        flask.session.pop(key, None)
        
    flask.session.pop('logged_in', None)
    for key in ('identity.name', 'identity.auth_type'):
        flask.session.pop(key, None)

#----------------------------------------------------------------------
@app.route('/logout')
def logout():
#----------------------------------------------------------------------
    # Remove the user information from the session
    user = authmodel.find_user(flask.session['user_id'])
    user.authenticated = False
    set_logged_out()

    # Tell Flask-Principal the user is anonymous
    principal.identity_changed.send(flask.current_app._get_current_object(),
                          identity=principal.AnonymousIdentity())

    return flask.redirect(flask.request.args.get('next') or flask.url_for('index'))

########################################################################
class ClubForm(flaskwtf.Form):
########################################################################
    club = wtforms.SelectField('Club',coerce=int)

#----------------------------------------------------------------------
@app.route('/setclub', methods=['GET', 'POST'])
@flasklogin.login_required
def setclub():
#----------------------------------------------------------------------
    # find session's user
    thisuser = flasklogin.current_user

    # define form
    form = ClubForm()
    form.club.choices = _getuserclubs(thisuser)

    # Validate form input for POST
    if flask.request.method == "POST" and form.validate_on_submit():
        # Retrieve the club picked by the user
        thisclubid = form.club.data
        club = Club.query.filter_by(id=thisclubid).first()
        flask.session['club_id'] = club.id
        flask.session['club_name'] = club.name
        
        # TODO: need to change this to clubconsole
        return flask.redirect(flask.request.args.get('next') or flask.url_for('ownerconsole'))
        
    return flask.render_template('setclub.html', form=form, pagename='Set Club', action='Set Club')


########################################################################
# permissions definition
########################################################################
# load principal extension, and define permissions
principals = principal.Principal(app)
owner_permission = principal.Permission(principal.RoleNeed('owner'))
#admin_permission = principal.Permission(principal.RoleNeed('admin'))
#viewer_permission = principal.Permission(principal.RoleNeed('viewer'))

ClubDataNeed = namedtuple('club_data', ['method', 'value'])
UpdateClubDataNeed = partial(ClubDataNeed,'update')
ViewClubDataNeed = partial(ClubDataNeed,'view')

class UpdateClubDataPermission(principal.Permission):
    def __init__(self, clubid):
        need = UpdateClubDataNeed(clubid)
        super(UpdateClubDataPermission, self).__init__(need)

class ViewClubDataPermission(principal.Permission):
    def __init__(self, clubid):
        need = ViewClubDataNeed(clubid)
        super(ViewClubDataPermission, self).__init__(need)


#----------------------------------------------------------------------
@principal.identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
#----------------------------------------------------------------------
    # Set the identity user object
    current_user = flasklogin.current_user
    identity.user = current_user
    if not current_user.is_authenticated():
        set_logged_out()

    # Add the UserNeed to the identity
    if hasattr(current_user, 'id'):
        identity.provides.add(principal.UserNeed(current_user.id))

    # Assuming the User model has a list of roles, update the
    # identity with the roles that the user provides
    if hasattr(current_user,'roles'):
        for role in current_user.roles:
            if role.name == 'viewer' or role.name == 'admin':
                identity.provides.add(ViewClubDataNeed(role.club.id))
            elif role.name == 'admin':
                identity.provides.add(UpdateClubDataNeed(role.club.id))
            elif role.name == 'owner':
                identity.provides.add(principal.RoleNeed('owner'))
                for club in authmodel.Club.query.all():
                    if club.name == 'owner': continue
                    identity.provides.add(ViewClubDataNeed(club.id))
                    identity.provides.add(UpdateClubDataNeed(club.id))
