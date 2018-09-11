# coding: utf8

import ast
import datetime
import hashlib
import math
import os.path
import random
import uuid
from binascii import a2b_base64
from decimal import Decimal, getcontext
from functools import wraps
from smtplib import SMTPException
from sqlite3 import IntegrityError, Error
from urllib.request import Request, urlopen
from xml.dom import minidom
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, g, request, make_response, redirect, session, Response, jsonify
# from flask_cors import CORS
from flask_mail import Mail, Message
from database import Database

now = datetime.datetime.now()
dayID = 1


def config_mail():
    config_list = []
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(my_path, 'conf.txt')
    with open(path) as c:
        for i in range(2):
            line = c.readline()
            options = line.split(':')
            # remove trailing '\n'
            option = options[1]
            option = option.rstrip()
            # list[0] = mail, list[1] = password
            config_list.append(option)
    return config_list


config_list = config_mail()
mail_default_sender = config_list[0]
mail_username = config_list[0]
mail_password = config_list[1]
app = Flask(__name__)
# cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config.update(
    DEBUG=False,
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME=mail_username,
    MAIL_DEFAULT_SENDER=mail_default_sender,
    MAIL_PASSWORD=mail_password
)
mail = Mail(app)

# GLOBAL_URL = "https://kajaja.herokuapp.com"
GLOBAL_URL = "http://127.0.0.1:5000"
ERR_PASSWORD = "Password or email invalid"
ERR_UNAUTH = "Please log in"
ERR_BLANK = "Empty query"
ERR_FORM = 'The form must be filled'
ERR_UNI_USER = "This username already exists, please choose another one"
ERR_NODATA = "Nous n'avons pas trouvé ce que vous cherchez"
ERR_SERVOR = "transaction was unsuccessfull"
ERR_NOPOST = "Vous n'avez pas d'annonce affichée"
ERR_404 = "This page does not exist"
INFO_MSG_SENT_ADOPTION = "An email has been sent."
INFO_MSG_SENT_RECOVERY = "Check you rmail box to recover your password."
INFO_MAIL_SUBJECT = "fxRates alert  "
INFO_MAIL_RECOVER_SUBJECT = "Recover your password"
INFO_MAIL_RECOVER_BODY = "follow this link http://localhost:5000/password_recovery/validate then enter this password : "



def db():
    db = getattr(g, '_database', None)
    if db is None:
        g._database = Database()
    return g._database


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.disconnect()


@app.template_filter('string_to_dict')
def string_to_dict(value):
    response = ast.literal_eval(value)
    return response


def authentication_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not is_authenticated(session):
            return send_unauthorized()
        return f(*args, **kwargs)

    return decorated


def is_authenticated(session):
    resp = 'id' in session
    return resp


def send_unauthorized():
    error = ERR_UNAUTH
    return render_template('user_login.html', error=error), 401
    # return Response('Could not verify your access level for that URL.\n''You have to login with proper credentials', 401,{'WWW-Authenticate': 'Basic realm="Login Required"'})


def get_username():
    if 'id' in session:
        return db().get_session_username_by_id_session(session['id'])
    return None


def is_time_to_update(date):
    ## TODO check heroku datetime
    if date.hour < 3 or date.hour > 17:
        return False
    return True


def check_rates(rates):
    my_rates = db().get_rates()
    if my_rates is None:
        db().insert_rates(rates)


@app.route('/')
@authentication_required
def start():
    rates = db().get_rates()
    if 'id' in session:
        return render_template('my_rates.html', rates=rates, id=get_username())
    return render_template('my_rates.html', rates=rates)


def get_current_rates():
    url = "https://rates.fxcm.com/RatesXML"
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    xml = urlopen(req)
    dom = minidom.parse(xml)
    xml_rates = dom.getElementsByTagName('Rate')
    rates = []
    symbol_preferences = ['EURCAD', 'EURUSD', 'EURAUD', 'EURCHF', 'AUDCAD', 'UADUSD', 'AUDCHF', 'USDCHF', 'USDCAD', 'CADCHF']
    date = now.strftime('%Y-%m-%d %H:%M')
    for rate in xml_rates:
        symbol = rate.attributes['Symbol'].value
        if symbol in symbol_preferences:
            bid = rate.getElementsByTagName('Bid')
            ask = rate.getElementsByTagName('Ask')
            bid = bid[0].firstChild.data
            ask = ask[0].firstChild.data
            # precision for Decimal type
            getcontext().prec = 8
            decimal_bid = Decimal(bid)
            decimal_ask = Decimal(ask)
            average = (decimal_bid + decimal_ask) / 2
            delta = decimal_bid - decimal_ask
            data = {'symbol': symbol, 'bid': float(bid), 'ask': float(ask), 'average': float(average), 'delta': str(delta), 'date_created': date}
            rates.append(data)
    # to populate db
    # db().insert_rates(rates)
    return rates


@app.route('/currentRates')
def current_rates():
    rates = get_current_rates()
    if 'id' in session:
        return render_template('my_rates.html', rates=rates, id=get_username())
    return render_template('my_rates.html', rates=rates)


@app.route('/dailyRates')
@authentication_required
def daily_rates():
    days = db().get_daily_rates()
    if 'id' in session:
        return render_template('daily_rates.html', days=days, id=get_username())
    return render_template('daily_rates.html', days=days)


@app.route('/dailyRates/<int:id>')
@authentication_required
def get_daily_rate(id):
    rate = db().get_daily_rate_by_id(id)
    if 'id' in session:
        return render_template('daily_rate.html', days=rate, id=get_username())
    return render_template('daily_rate.html', days=rate)


@app.route('/<symbol>')
@authentication_required
def get_symbol(symbol):
    symbol_preferences = ['EURCAD', 'EURUSD', 'EURAUD', 'EURCHF', 'AUDCAD', 'UADUSD', 'AUDCHF', 'USDCHF', 'USDCAD', 'CADCHF']
    if symbol in symbol_preferences:
        rates = db().get_rates_like(symbol)
        return render_template('my_rate_by_symbol.html', rates=rates)
    return render_template('404.html', error=ERR_404), 404


def update_rates():
    if is_time_to_update(now):
        with app.app_context():
            my_rates = db().get_rates()
            current_rates = get_current_rates()
            for one_of_my_rate in my_rates:
                for one_of_current_rates in current_rates:
                    if one_of_my_rate['symbol'] == one_of_current_rates['symbol']:
                        if one_of_my_rate['bid'] != one_of_current_rates['bid'] or one_of_my_rate['ask'] != one_of_current_rates['ask']:
                            db().update_rate(one_of_current_rates)


def update_daily_rates():
    global dayID
    if dayID == 76:
        dayID = 1
    with app.app_context():
        my_rates = db().get_rates()
        date_created = now.strftime('%Y-%m-%d')
        db().update_daily_rates(dayID, my_rates, date_created)
        dayID += 1


@app.route('/image/<pic_id>.jpeg')
def download_picture(pic_id):
    binary_data = db().get_pictures_imgdata(pic_id)
    if binary_data is None:
        return Response(status=404)
    else:
        response = make_response(binary_data)
        response.headers.set('Content-Type', 'image/jpeg')
    return response


@app.route('/search', methods=['POST'])
def get_rates_by_query():
    query = request.json['query']
    filter = int(request.json['filter'])

    if request_data_is_invalid(query=query):
        return jsonify({'success': False, 'error': ERR_BLANK}), 204

    if filter == 0:
        filter = 'all'
    elif filter == 1:
        filter = 'dogs'
    elif filter == 2:
        filter = 'cats'
    elif filter == 3:
        filter = 'other'
    else:
        filter = 'all'

    redirect_url = GLOBAL_URL + '/search/' + query + '/1' + '?filter=' + filter
    return jsonify({'success': True, 'url': redirect_url, 'filter': filter}), 200


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.json['username']
        password = request.json['password']

        # data validation
        if request_data_is_invalid(username=username, password=password):
            return jsonify({'success': False, 'error': ERR_FORM}), 400

        user = db().get_user_hash_by_username(username)
        if user is None:
            redirect_url = GLOBAL_URL + '/login'
            return jsonify({'success': False, 'url': redirect_url,'error': ERR_PASSWORD}), 401

        salt = user[0]
        hashed_password = hashlib.sha512(
            str(password + salt).encode('utf-8')).hexdigest()
        if hashed_password == user[1]:
            id_session = uuid.uuid4().hex
            db().save_session(id_session, username)
            session['id'] = id_session
            redirect_url = GLOBAL_URL + '/myaccount'
            return jsonify({'success': True, 'url': redirect_url}), 200
        else:
            redirect_url = GLOBAL_URL + '/login'
            return jsonify({'success': False, 
                            'url': redirect_url,
                            'error': ERR_PASSWORD}), 401
    else:
        return render_template('user_login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.json['username']
        password = request.json['password']
        email = request.json['email']

        if request_data_is_invalid(username=username, password=password, email=email):
            return jsonify({'success': False, 'error': ERR_FORM}), 400
        else:
            try:
                salt = uuid.uuid4().hex
                hashed_password = hashlib.sha512(str(password + salt).encode('utf-8')).hexdigest()
                db().create_user(username, email, salt, hashed_password)
                id_session = uuid.uuid4().hex
                db().save_session(id_session, username)
                session['id'] = id_session
                url = GLOBAL_URL + '/myaccount'

                return jsonify({'success': True, 'url': url}), 201
            # Unique constraint must be respected
            except IntegrityError:
                return jsonify({'success': False, 'error': ERR_UNI_USER}), 403
    else:
        return render_template('user_register.html'), 200


@app.route('/logout')
@authentication_required
def logout():
    if 'id' in session:
        id_session = session['id']
        session.pop('id', None)
        db().delete_session(id_session)
    return redirect('/')



def request_data_is_invalid(**kwargs):
    for key, value in kwargs.items():
        if value == '':
            return True
    return False


@app.route('/myaccount/', methods=['GET', 'UPDATE'])
@authentication_required
def get_myaccount():
    if request.method == 'GET':
        user_info = db().get_user_info_by_username(get_username())
        if user_info is None:
            return render_template('my_rates.html', error=ERR_UNAUTH), 204
        else:
            return render_template('myaccount.html', id=get_username(), infos=user_info), 200
    elif request.method == 'UPDATE':
        username = request.json['username']
        password = request.json['password']

        if request_data_is_invalid(username=username, password=password):
            return jsonify({'success': False, 'error': ERR_FORM}), 400

        try:
            session_username = get_username()
            email = db().get_user_email_by_username(get_username())

            id = db().get_user_id_by_id_session(session['id'])
            salt = uuid.uuid4().hex
            hashed_password = hashlib.sha512(str(password + salt).encode('utf-8')).hexdigest()

            db().update_user(id, username, email, salt, hashed_password, session_username)
            return_url = GLOBAL_URL + '/myaccount'
            return jsonify({'success': True, 'url': return_url}), 201
        except IntegrityError:
            return jsonify({'success': False, 'error': ERR_UNI_USER}), 403


def user_has_already_posted(user_id):
    rates = db().get_rates_by_owner_id(user_id)
    if len(rates):
        return True
    return False


def save_image_on_disc(**kwargs):
    user_id = kwargs['user_id']
    img_uri = kwargs['img_uri']
    name = kwargs['name']
    img_name = name + '_' + str(user_id)

    # front end send data_uri as data:image/base64,XXX
    # where xxx is the blob in string format
    listed_img_uri = img_uri.split(',')
    img_base64_tostring = listed_img_uri[1]

    # convert string to binary data for writing purpose
    binary_data = a2b_base64(img_base64_tostring)

    # allow to run on other machine thus we dont know the root path
    my_path = os.path.abspath(os.path.dirname(__file__))
    # TODO add image extention possibilities
    img_url = 'static/img/%s.jpeg' % (img_name,)
    path = os.path.join(my_path, img_url)

    # create/save image
    with open(path, 'wb+') as fh:
        fh.write(binary_data)
    return path


@app.route('/password_recovery', methods=['POST', 'GET'])
def password_recovery():
    if request.method == 'POST':
        smtp_response_ok = send_recovery_email()
        if smtp_response_ok:
            return jsonify({'success': True, 'msg': INFO_MSG_SENT_RECOVERY}), \
                   200
        else:
            return jsonify({'success': False, 'error': ERR_SERVOR}), 500
    elif request.method == 'GET':
        return render_template('password_recovery.html')


def send_recovery_email():
    user_email = request.json['email']
    username = db().get_user_username_by_email(user_email)
    if username:
        token = generate_token()
        date = now.strftime('%Y-%m-%d')
        db().create_account(username, user_email, token, date)
        subject = INFO_MAIL_RECOVER_SUBJECT
        msg = Message(subject, recipients=[user_email])
        msg.body = INFO_MAIL_RECOVER_BODY + token
        try:
            mail.send(msg)
        except SMTPException:
            return False
        return True
    # return true even if email was not sent
    return True


def generate_token():
    # generate 5 random number
    list_of_ints = random.sample(range(1, 10), 5)
    new_password = ''.join(str(x) for x in list_of_ints)
    return new_password


@app.route('/password_recovery/validate', methods=['POST', 'GET'])
def password_recovery_validate():
    if request.method == 'POST':
        username = request.json['username']
        password = request.json['password']
        token = db().get_account_token_by_username(username)
        if token is None:
            redirect_url = GLOBAL_URL + '/password_recovery/validate'
            return jsonify({'success': False, 
                            'url': redirect_url,
                            'error': ERR_PASSWORD}), 401

        if password == token:
            # update user
            infos = db().get_user_info_by_username(username)
            user_id = infos[0]
            salt = uuid.uuid4().hex
            hashed_password = hashlib.sha512(str(token + salt).encode('utf-8')).hexdigest()
            db().update_user_password(user_id, salt, hashed_password)
            # delete account
            db().delete_account_by_username(username)
            # update session
            id_session = uuid.uuid4().hex
            db().save_session(id_session, username)
            session['id'] = id_session
            redirect_url = GLOBAL_URL + '/myaccount'
            return jsonify({'success': True, 'url': redirect_url}), 201
        else:
            redirect_url = GLOBAL_URL + '/password_recovery/validate'
            return jsonify({'success': False,
                            'url': redirect_url,
                            'error': ERR_PASSWORD}), 401
    else:
        return render_template('password_recovery_validate.html')


@app.route('/send_email', methods=['POST'])
def send_email():
    sender_email = request.json['email']
    msg_body = request.json['message']
    animal_id = request.json['animal_id']
    subject = INFO_MAIL_SUBJECT + sender_email

    if request_data_is_invalid(sender_email=sender_email, animal_id=animal_id):
        return jsonify({'success': False, 'error': ERR_FORM}), 400

    recipient = db().get_user_email_by_animal_id(animal_id)
    msg = Message(subject, recipients=[recipient])
    msg.body = msg_body
    try:
        mail.send(msg)
    except SMTPException:
        return jsonify({'success': False, 'error': ERR_SERVOR}), 500
    return jsonify({'success': True, 'msg': INFO_MSG_SENT_ADOPTION}), 200


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', error=ERR_404), 404


app.secret_key = '(*&*&322387he738220)(*(*22347657'

if __name__ == '__main__':
    sched = BackgroundScheduler()
    sched.add_job(update_rates, 'interval', minutes=15)
    sched.add_job(update_daily_rates, 'cron', hour=14, minute=24)
    # sched.add_job(update_daily_rates, 'interval', minutes=.1)
    sched.start()
    app.run(use_reloader=False)
