###########################################################################################
# raceresultswebapp.userrole - user/role views for race results web application
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

# pypi
import flask
import flask.ext.login as flasklogin
import flask.ext.principal as principal
import flask.ext.wtf as flaskwtf
import wtforms

# home grown
from raceresultswebapp import app, authmodel
from raceresultswebapp.login import owner_permission, ClubDataNeed, UpdateClubDataNeed, ViewClubDataNeed, \
                                    UpdateClubDataPermission, ViewClubDataPermission
from raceresultswebapp.login import getnavigation
db = authmodel.db

# module specific needs
from authmodel import User, Role, Club

########################################################################
class UserForm(flaskwtf.Form):
########################################################################
    email = wtforms.StringField('Email')
    name = wtforms.StringField('Name')
    password = wtforms.StringField('Password')
    owner = wtforms.BooleanField('Owner')
    club = wtforms.SelectField('Club',coerce=int)
    admin = wtforms.BooleanField('Admin')
    viewer = wtforms.BooleanField('Viewer')
    hidden_userid = wtforms.HiddenField()
    
########################################################################
class NewUserForm(flaskwtf.Form):
########################################################################
    email = wtforms.StringField('Email')
    name = wtforms.StringField('Name')
    password = wtforms.StringField('Password')
    owner = wtforms.BooleanField('Owner')
    
########################################################################
# Manage Users
########################################################################
#----------------------------------------------------------------------
@app.route('/manageusers')
@flasklogin.login_required
@owner_permission.require()
def manageusers():
#----------------------------------------------------------------------
    users = []
    for user in User.query.all():
        users.append((user.name,user)) # sort by name
    users.sort()
    users = [user[1] for user in users]
    
    return flask.render_template('manageusers.html',users=users)

#----------------------------------------------------------------------
@app.route('/newuser', methods=['GET', 'POST'])
@flasklogin.login_required
@owner_permission.require()
def newuser():
#----------------------------------------------------------------------
    # create the form
    form = NewUserForm()

    # set up buttons
    buttontext = 'Add'
    
    # nothing to do for GET yet
    if flask.request.method == "GET":
        pass
    
    # validate form input
    elif flask.request.method == "POST":
        if form.validate_on_submit():
            # action and commit requested
            if flask.request.form['whichbutton'] == buttontext:
                thisuser = User(form.email.data, form.name.data, form.password.data)
                print 'form.owner.data={}'.format(form.owner.data)
                
                db.session.add(thisuser)
                db.session.commit()
                flask.get_flashed_messages()    # clears flash queue
                return flask.redirect(flask.url_for('useraction',userid=thisuser.id,action='edit'))

            # cancel requested - note changes may have been made in url_for('_setpermission') which need to be rolled back
            elif flask.request.form['whichbutton'] == 'Cancel':
                db.session.expunge_all() # throw out any changes which have been made
                return flask.redirect(flask.url_for('manageusers'))
    
    return flask.render_template('ownermanageuser.html', form=form, thispagename='New User', action=buttontext, newuser=True)

#----------------------------------------------------------------------
@app.route('/user/<userid>/<action>', methods=['GET','POST'])
@flasklogin.login_required
@owner_permission.require()
def useraction(userid,action):
#----------------------------------------------------------------------
    '''
    handle user record actions
    
    :param userid: user id
    :param action: 'delete' or 'edit'
    '''
    # get the user from the database
    thisuser = authmodel.User.query.filter_by(id=userid).first()

    if action == 'delete':
        pagename = 'Delete User'
        buttontext = 'Delete'
        flask.flash('Confirm delete by pressing Delete button')
        successtext = '{} deleted'.format(thisuser.name)
        displayonly = True
    elif action == 'edit':
        pagename = 'Edit User'
        buttontext = 'Update'
        successtext = '{} updated'.format(thisuser.name)
        displayonly = False
    else:
        flask.abort(404)

    # create the form
    form = UserForm(email=thisuser.email, name=thisuser.name)
    form.hidden_userid.data = userid
    form.club.choices = [(0,'Select Club')] + [(club.id,club.name) for club in Club.query.order_by('name') if club.name != 'owner']

    # define form for GET
    if flask.request.method == "GET":
        form.owner.data = False
        for role in thisuser.roles:
            if role.name == 'owner':
                form.owner.data = True
                break
        form.admin.data = False
        form.viewer.data = False
    
    # validate form input
    elif flask.request.method == "POST":
        if form.validate_on_submit():
            flask.get_flashed_messages()    # clears flash queue

            # action and commit requested
            if flask.request.form['whichbutton'] == buttontext:
                if action == 'delete':
                    db.session.delete(thisuser)
                elif action =='edit':
                    thisuser.email = form.email.data
                    thisuser.name = form.name.data
                    if form.password.data:
                        thisuser.set_password(form.password.data)
                db.session.commit()
                return flask.redirect(flask.url_for('manageusers'))
            
            # cancel requested - note changes may have been made in url_for('updatepermissions') which need to be rolled back
            elif flask.request.form['whichbutton'] == 'Cancel':
                db.session.expunge_all() # throw out any changes which have been made
                return flask.redirect(flask.url_for('manageusers'))
    
    return flask.render_template('ownermanageuser.html', form=form,
                                 userurl=flask.url_for('useraction',userid=userid,action=action),
                                 displayonly=displayonly,
                                 thispagename=pagename, action=buttontext)

#----------------------------------------------------------------------
def _setpermission(club,user,rolename,setrole):
#----------------------------------------------------------------------
    '''
    sets (or resets) a permission, but does not commit to the database
    
    :param club: club database object
    :param user: user database object
    :param rolename: name of role
    :param setrole: True to add the permission or False to remove it
    
    :rtype: boolean indicating success (True) or failure (False)
    '''
    # get the role
    thisrole = Role.query.filter_by(club_id=club.id, name=rolename).first()
    
    # not found -- shouldn't happen
    if not thisrole:
        return False
    
    # adding the permission
    if setrole:
        if thisrole not in user.roles:
            print '{} not in {}: trying to add role'.format(thisrole,user.roles)
            user.roles.append(thisrole)
    
    # removing the permission
    else:
        if thisrole in user.roles:
            print '{} in {}: trying to remove role'.format(thisrole,user.roles)
            user.roles.remove(thisrole)
    
    return True

#----------------------------------------------------------------------
@app.route('/_setpermission')
@flasklogin.login_required
@owner_permission.require()
def _set_permission():
#----------------------------------------------------------------------
    '''
    ajax server side to set a permission on an existing user
    
    does not commit as this is done when the form is saved
    '''
    clubid = flask.request.args.get('clubid',0,type=int)
    userid = flask.request.args.get('userid',0,type=int)
    rolename = flask.request.args.get('rolename','')
    setrole = flask.request.args.get('setrole','false')=='true'
    
    if userid==0 or rolename=='':
        return flask.jsonify(False)
    
    # get the user and club
    thisuser = User.query.filter_by(id=userid).first()
    if rolename == 'owner':
        thisclub = Club.query.filter_by(name='owner').first()
    else:
        thisclub = Club.query.filter_by(id=clubid).first()
    
    # handle setting of permission for this club in the user object
    success = _setpermission(thisclub,thisuser,rolename,setrole)
    
    return flask.jsonify(success=success)
    
#----------------------------------------------------------------------
@app.route('/_getpermissions')
@flasklogin.login_required
@owner_permission.require()
def _get_permissions():
#----------------------------------------------------------------------
    '''
    ajax server side to get permissions for an existing user/club
    '''
    clubid = flask.request.args.get('clubid',0,type=int)
    userid = flask.request.args.get('userid',0,type=int)
    
    # get the user and club
    thisuser = User.query.filter_by(id=userid).first()

    # set up false permissions
    # NOTE: permissions need to match authmodel.rolenames
    admin = False
    viewer = False
    
    if clubid != 0 and thisuser:
        for role in thisuser.roles:
            if role.club_id == clubid:
                if   role.name == 'admin':  admin = True
                elif role.name == 'viewer': viewer = True
            
    return flask.jsonify(admin=admin,viewer=viewer)
    
