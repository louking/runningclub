###########################################################################################
# raceresultswebapp.club - club views for race results web application
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
from authmodel import Club, Role

########################################################################
class OwnerClubForm(flaskwtf.Form):
########################################################################
    shname = wtforms.StringField('Short Name')
    name = wtforms.StringField('Full Name')
    
########################################################################
# Manage Clubs
########################################################################
#----------------------------------------------------------------------
@app.route('/manageclubs')
@owner_permission.require()
def manageclubs():
#----------------------------------------------------------------------
    clubs = []
    for club in Club.query.all():
        if club.shname == 'owner': continue # not really a club -- TODO: IS THIS Club entry NEEDED?
                                            # if remove owner from club table, will that cause an issue in the role table?
        clubs.append(club)

    return flask.render_template('manageclubs.html',clubs=clubs)

#----------------------------------------------------------------------
@app.route('/newclub', methods=['GET', 'POST'])
@owner_permission.require()
def newclub():
#----------------------------------------------------------------------
    # create form
    form = OwnerClubForm()

    # nothing to do on GET so far
    if flask.request.method == "GET":
        pass
    
    # validate form input
    elif flask.request.method == "POST":
        if form.validate_on_submit():
            thisclub = Club()
            thisclub.shname = form.shname.data
            thisclub.name = form.name.data
            
            # add club
            db.session.add(thisclub)
            
            # add roles to club
            for rolename in authmodel.rolenames:
                role = Role(rolename)
                thisclub.roles.append(role)
            
            db.session.commit()
            
            flask.get_flashed_messages()    # clears flash queue
            return flask.redirect(flask.url_for('manageclubs'))
    
    return flask.render_template('ownermanageclub.html', form=form, thispagename='New Club', action='Add')

#----------------------------------------------------------------------
@app.route('/club/<clubname>/<action>', methods=['GET','POST'])
@owner_permission.require()
def clubaction(clubname,action):
#----------------------------------------------------------------------
    '''
    handle club record actions
    
    :param clubname: short name of club
    :param action: 'delete' or 'edit'
    '''
    # get the data from the database
    thisclub = authmodel.Club.query.filter_by(shname=clubname).first()

    if action == 'delete':
        pagename = 'Delete Club'
        buttontext = 'Delete'
        flask.flash('Confirm delete by pressing Delete button')
        successtext = '{} deleted'.format(thisclub.shname)
        displayonly = True
    elif action == 'edit':
        pagename = 'Edit Club'
        buttontext = 'Update'
        successtext = '{} updated'.format(thisclub.shname)
        displayonly = False
    else:
        flask.abort(404)

    # create form
    form = OwnerClubForm(shname=thisclub.shname, name=thisclub.name)

    # nothing to do on GET so far
    if flask.request.method == "GET":
        pass
    
    # validate form input
    elif flask.request.method == "POST":
        if form.validate_on_submit():
            flask.get_flashed_messages()    # clears flash queue
            if action == 'delete':
                db.session.delete(thisclub)
            elif action =='edit':
                thisclub.shname = form.shname.data
                thisclub.name = form.name.data
            db.session.commit()
            return flask.redirect(flask.url_for('manageclubs'))
    
    return flask.render_template('ownermanageclub.html', form=form,
                                 cluburl=flask.url_for('clubaction',clubname=clubname,action=action),
                                 displayonly=displayonly,
                                 thispagename=pagename, action=buttontext)

