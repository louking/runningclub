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

login_manager = flasklogin.LoginManager(app)

#----------------------------------------------------------------------
def getnavigation(clubid,rolenames):
#----------------------------------------------------------------------
    '''
    retrieve navigation list, based on current club and user's roles
    
    :param clubid: club id
    :param rolenames: list of role names
    :rettype: list of dicts {'display':navdisplay,'url':navurl}
    '''
    navigation = []
    
    navigation.append({'display':'Home','url':flask.url_for('index')})
    
    if 'owner' in rolenames:
        navigation.append({'display':'Manage Clubs','url':flask.url_for('manageclubs')})
        navigation.append({'display':'Manage Users','url':flask.url_for('ownermanageusers')})
        
    return navigation

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

    # Validate form input
    if form.validate_on_submit():
        # Retrieve the user from the datastore
        user = authmodel.find_user(form.email.data)
        if user == None:
            return flask.render_template('login.html', form=form, error='username or password invalid')

        # Compare passwords (use password hashing production)
        if user.check_password(form.password.data):
            # Keep the user info in the session using Flask-Login
            flasklogin.login_user(user)
            user.authenticated = True   # else @login_required will fail
            flask.session['logged_in'] = True

            # Tell Flask-Principal the identity changed
            principal.identity_changed.send(
                flask.current_app._get_current_object(),
                identity=principal.Identity(user.id))
            
            return flask.redirect(flask.request.args.get('next') or flask.url_for('membersonly'))
        
        else:
            return flask.render_template('login.html', form=form, error='username or password invalid')

    return flask.render_template('login.html', form=form)

########################################################################
########################################################################
#----------------------------------------------------------------------
def set_logged_out():
#----------------------------------------------------------------------
    flasklogin.logout_user()
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
    #flasklogin.logout_user()
    #flask.session.pop('logged_in', None)
    #flask.session.pop('nav', None)
    #        
    ## Remove session keys set by Flask-Principal
    #for key in ('identity.name', 'identity.auth_type'):
    #    flask.session.pop(key, None)

    # Tell Flask-Principal the user is anonymous
    principal.identity_changed.send(flask.current_app._get_current_object(),
                          identity=principal.AnonymousIdentity())

    return flask.redirect(flask.request.args.get('next') or flask.url_for('index'))

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
                    if club == 'owner': continue
                    identity.provides.add(ViewClubDataNeed(club.id))
                    identity.provides.add(UpdateClubDataNeed(club.id))
                
    # get navigation list - should this be in on_identity_changed ?
    # TODO: get actual data from user's roles 
    if current_user.is_authenticated():
        nav = getnavigation(1,['owner','admin','viewer'])
    else:
        nav = getnavigation(0,[])
    flask.session['nav'] = nav
            
