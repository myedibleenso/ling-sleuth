from flask import render_template, flash, redirect, session, url_for, request, g, make_response, send_file, abort, send_from_directory, Response, Markup
from flask.ext.login import login_user , logout_user , current_user , login_required
from app import app, db, login_manager
from .forms import LoginForm, RegisterForm
from .models import User
from config import basedir
from authomatic.adapters import WerkzeugAdapter
from config import authomatic #used for oauth2 stuff
import os
import logging

UPLOADS_DIR = os.path.join(basedir, app.config['UPLOAD_FOLDER'])


# who is the current user?
@app.before_request
def before_request():
    g.user = current_user

# for handling user data
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',
                           title='Welcome')

@app.route('/login/<provider_name>/', methods=['GET', 'POST'])
def login_with_provider(provider_name):
    """
    Login handler, must accept both GET and POST to be able to use OpenID.
    """
    print "CONFIG info:\n{}".format(app.config["CONFIG"])
    # We need response object for the WerkzeugAdapter.
    response = make_response()

    # Log the user in, pass it the adapter and the provider name.
    result = authomatic.login(WerkzeugAdapter(request, response), provider_name)

    # If there is no LoginResult object, the login procedure is still pending.
    if result:
        if result.user:
            # We need to update the user to get more info.
            result.user.update()
            handle_user(result)
            # TODO: register user if needed.
            app.logger.info("{0} is a logged in via {1}.".format(result.user.name, provider_name))
        # The rest happens inside the template.
        #result.user.data.x will return further user data
        return render_template('login-test.html', result=result)

    # Don't forget to return the response.
    return response

@app.route('/login',methods=['GET','POST'])
def login():
    # Choose a login provider
    return render_template('login.html')



@app.route('/logout')
def logout():
    logout_user()
    flash("Bye for now!")
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(error):
    return 'This page does not exist', 404

#@app.errorhandler(DatabaseError)
#def special_exception_handler(error):
#    return 'Database connection failed', 500


###Other stuff

@app.route('/about')
def about():
    return render_template('about.html',
                           title='About')

@app.route('/profile')
@login_required
def profile():
     return render_template('profile.html',
                           title='Profile')

@app.route('/cases')
def cases():
    return render_template('cases.html',
                           title='Cases')

@app.route('/learn')
def learn():
    return render_template('learn.html',
                           title='Learn')

@app.route('/knowledge')
@login_required
def knowledge():
    return render_template('knowledge.html',
                           title='Unlocked Skillz!')

@app.route('/downloads/<filename>')
def serve_file(filename):
    return Response(open(os.path.join(UPLOADS_DIR, filename), 'rb').read(),
                       mimetype="text/plain",
                       headers={"Content-Disposition":
                                    "attachment;filename={0}".format(filename)})


def handle_user(result):
    # is the user registered?
    registered_user = User.query.filter(User.username == result.user.name, User.email == result.user.email).first()
    # register if necessary...
    if not registered_user:
        registered_user = register_user(result)
        db.session.add(user)
        db.session.commit()
    login_user(registered_user)

if __name__ == '__main__':
    app.debug = True
    app.run()
