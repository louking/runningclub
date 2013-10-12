###########################################################################################
# raceresultswebapp - package
#
#       Date            Author          Reason
#       ----            ------          ------
#       10/03/13        Lou King        Create
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
import os

# pypi
import flask
import flask.ext.login as flasklogin
import flask.ext.principal as principal
import flask.ext.wtf as flaskwtf
import wtforms

#from flask import Flask, current_app, request, session, g, redirect, url_for, \
#     abort, render_template, flash
#from flask.ext.login import LoginManager, login_user, logout_user, \
#     login_required, current_user
#from flask.ext.wtf import Form
#from wtforms import StringField, PasswordField
#from flask.ext.principal import Principal, Identity, AnonymousIdentity, \
#     identity_changed

# homegrown
import authmodel

DEBUG = True
SECRET_KEY = 'flask development key'
#SECRET_KEY = os.urandom(24)

app = flask.Flask(__name__)
app.config.from_object(__name__)
db = authmodel.db

# import all views
import raceresultswebapp.login
import raceresultswebapp.club

# permissions
from raceresultswebapp.login import owner_permission, ClubDataNeed, UpdateClubDataNeed, ViewClubDataNeed, \
                                    UpdateClubDataPermission, ViewClubDataPermission
from raceresultswebapp.login import getnavigation
            
#@app.before_request
#def before_request():
#    flask.g.db = authmodel.db
#
#@app.teardown_request
#def teardown_request(exception):
#    db = getattr(flask.g, 'db', None)
#    if db is not None:
#        db.session.commit()

########################################################################
########################################################################
#----------------------------------------------------------------------
@app.route('/')
def index():
#----------------------------------------------------------------------
    return flask.render_template('index.html')

########################################################################
########################################################################
#----------------------------------------------------------------------
@app.route('/manageusers')
def ownermanageusers():
#----------------------------------------------------------------------
    return flask.render_template('ownermanageusers.html')

########################################################################
########################################################################
#----------------------------------------------------------------------
@app.route('/membersonly')
@flasklogin.login_required
def membersonly():
#----------------------------------------------------------------------
    return flask.render_template('members.html')

#----------------------------------------------------------------------
# main processing - run application
#----------------------------------------------------------------------
if __name__ == '__main__':
    app.run()