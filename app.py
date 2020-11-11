#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request, jsonify
# from flask.ext.sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import *
import os
import requests, json

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
#db = SQLAlchemy(app)

# Automatically tear down SQLAlchemy.
'''
@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()
'''

# Login required decorator.
'''
def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap
'''
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def home():
    return render_template('pages/placeholder.home.html')


@app.route('/about')
def about():
    return render_template('pages/placeholder.about.html')


@app.route('/login')
def login():
    form = LoginForm(request.form)
    return render_template('forms/login.html', form=form)


@app.route('/register')
def register():
    form = RegisterForm(request.form)
    return render_template('forms/register.html', form=form)


@app.route('/forgot')
def forgot():
    form = ForgotForm(request.form)
    return render_template('forms/forgot.html', form=form)

@app.route("/ask", methods=["POST"])
def ask():
    #Step by step:
    #0. Change chit chat into professional
    #1. Greetings
    #2. Response Inquiry
    #2.a Unkown queries: (Mou ikkai onegaishimasu)
    #2.b Call Luis to generate metadata, use to hit QnA Maker
    #3. Detect mou ii no youna hanashi ga attara, shitsureishimasu itte

    query = request.form.get('query')

    if query == "START":
        response_text = "初めまして！チャットボットと申します。問い合わせはどうぞ！"
    else:
        url = 'https://chatbot-kokoro.azurewebsites.net/qnamaker/knowledgebases/f2a8edcd-2631-497b-98e4-918663e299d0/generateAnswer'
        data = "{'question': '"+query+"'}"
        header = {'content-type': 'application/json', 'authorization': 'EndpointKey 30168be7-2ad2-4346-af8c-83fcc05069eb'}

        response = requests.post(url, data=data.encode("utf-8"), headers= header)
        response_text = json.loads(response.text)["answers"][0]["answer"]
        if "KB" in response_text:
            response_text = "恐れ入りますが、もう一回お願いします。"
    

    payload = json.dumps({
        'answer': response_text,
        'Access-Control-Allow-Origin':  'http://127.0.0.1:5000',
        'Access-Control-Allow-Methods': 'POST',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }, ensure_ascii=False)
    print(response_text)
    return payload


# Error handlers.


@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    # app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    # app.logger.addHandler(file_handler)
    # app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
