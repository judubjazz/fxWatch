# coding: utf8

from flask import Flask
from flask import render_template
from flask import g
from flask import request
from flask import make_response
from flask import redirect
from flask import session
from flask import Response
from flask import jsonify
# from flask_cors import CORS
from flask_mail import Mail, Message
from database import Database
from functools import wraps
from binascii import a2b_base64
from smtplib import SMTPException
import hashlib
import uuid
import io
import os.path
import datetime
import random
import math
from sqlite3 import IntegrityError, Error


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
    DEBUG=True,
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME=mail_username,
    MAIL_DEFAULT_SENDER=mail_default_sender,
    MAIL_PASSWORD=mail_password
)
mail = Mail(app)

ERR_PASSWORD = "Mot de passe ou nom d'utilisateur incorrect"
ERR_UNAUTH = "Vous devez vous connecter pour avoir accès à cette page"
ERR_BLANK = "Recherche vide"
ERR_FORM = 'Le formulaire doit être rempli'
ERR_UNI_USER = "Le nom d'utilisateur existe déjà, choississez un autre nom"
ERR_UNI_POST = "Vous avez déjà un animal en attente d'adoption"
ERR_NODATA = "Nous n'avons pas trouvé ce que vous cherchez"
ERR_SERVOR = "La transaction n'a pas été effectuée"
ERR_NOPOST = "Vous n'avez pas d'annonce affichée"
ERR_404 = "Cette page n'existe pas"

INFO_DEL = "Votre annonce a été supprimée"
INFO_MSG_SENT_ADOPTION = "Un email a été envoyé au propriétaire."\
                         " Souvenez-vous ! " \
                         "Adopter un animal est un contract à vie."
INFO_MSG_SENT_RECOVERY = "Récupérer votre mot de passe" \
                         " dans votre boite à courriels"
INFO_MAIL_SUBJECT = "Quelqu'un est interressé  à adopter votre animal," \
                    " contacter >>  "
INFO_MAIL_RECOVER_SUBJECT = "Récupérer votre mot de passe"
INFO_MAIL_RECOVER_BODY = "Suivez ce lien " \
                         "http://localhost:5000/password_recovery/validate " \
                         "et connectez-vous avec ce mot de passe : "


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        g._database = Database()
    return g._database


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.disconnect()


@app.template_filter('b64decode')
def b64decode(value):
    print(value)
    resp = io.StringIO(value['bin'])
    return resp


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
    # return Response('Could not verify your access level for that URL.\n'
    #                 'You have to login with proper credentials', 401,
    #                 {'WWW-Authenticate': 'Basic realm="Login Required"'})


def get_username():
    if 'id' in session:
        return get_db().get_session_username_by_id_session(session['id'])
    return None


@app.route('/')
def start():
    animals_random = get_db().get_five_random_animals()

    if 'id' in session:
        return render_template('index.html', animals=animals_random,
                               id=get_username())
    return render_template('index.html', animals=animals_random)


@app.route('/image/<pic_id>.jpeg')
def download_picture(pic_id):
    db = get_db()
    binary_data = db.get_pictures_imgdata(pic_id)
    if binary_data is None:
        return Response(status=404)
    else:
        response = make_response(binary_data)
        response.headers.set('Content-Type', 'image/jpeg')
    return response


@app.route('/search', methods=['POST'])
def get_animals_by_query():
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

    redirect_url = 'http://localhost:5000/search/' \
                   + query + '/1' + '?filter=' + filter
    return jsonify(
        {'success': True, 'url': redirect_url, 'filter': filter}), 200


@app.route('/search/<query>/<int:page>', methods=['GET'])
def get_animals_by_page(query, page):
    filter = request.args.get('filter')
    data = get_db().get_animals_like_query(query, filter)

    # TODO optimize to not fetch all data
    nb_page = math.ceil(len(data) / 5)
    # page number verification
    if page > nb_page:
        page = nb_page
    elif page < 1:
        page = 1

    # 5 images per page
    end = page * 5
    start = end - 5
    animals = data[start:end]

    return render_template('search_results.html', animals=animals,
                           id=get_username(), query=query,
                           nb_page=nb_page), 200


@app.route('/animals/<int:animal_id>', methods=['GET'])
def get_animal_by_id(animal_id):
    animals = get_db().get_animals_by_id(animal_id)
    username = get_username()
    if animals is None:
        return render_template('search_result_by_id.html',
                               error='no results'), 204
    else:
        return render_template('search_result_by_id.html', animals=animals,
                               id=username), 200


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.json['username']
        password = request.json['password']

        # data validation
        if request_data_is_invalid(username=username, password=password):
            return jsonify({'success': False, 'error': ERR_FORM}), 400

        user = get_db().get_user_hash_by_username(username)
        if user is None:
            redirect_url = 'http://localhost:5000/login'
            return jsonify({'success': False, 'url': redirect_url,
                            'error': ERR_PASSWORD}), 401

        salt = user[0]
        hashed_password = hashlib.sha512(
            str(password + salt).encode('utf-8')).hexdigest()
        if hashed_password == user[1]:
            id_session = uuid.uuid4().hex
            get_db().save_session(id_session, username)
            session['id'] = id_session
            redirect_url = 'http://localhost:5000/myaccount'
            return jsonify({'success': True, 'url': redirect_url}), 200
        else:
            redirect_url = 'http://localhost:5000/login'
            return jsonify({'success': False, 'url': redirect_url,
                            'error': ERR_PASSWORD}), 401
    else:
        return render_template('user_login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.json['username']
        name = request.json['name']
        family_name = request.json['family_name']
        phone = request.json['phone']
        address = request.json['address']
        password = request.json['password']
        email = request.json['email']

        # data validation
        if request_data_is_invalid(username=username, name=name,
                                   family_name=family_name, phone=phone,
                                   address=address, password=password,
                                   email=email):
            return jsonify({'success': False, 'error': ERR_FORM}), 400
        else:
            try:
                salt = uuid.uuid4().hex
                hashed_password = hashlib.sha512(
                    str(password + salt).encode('utf-8')).hexdigest()
                get_db().create_user(username, name, family_name, phone,
                                     address, email, salt, hashed_password)
                id_session = uuid.uuid4().hex
                get_db().save_session(id_session, username)
                session['id'] = id_session
                url = 'http://localhost:5000/myaccount'

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
        get_db().delete_session(id_session)
    return redirect('/')


@app.route('/mypet', methods=['GET'])
@authentication_required
def mypet():
    if request.method == 'GET':
        id = get_db().get_user_id_by_id_session(session['id'])
        animals = get_db().get_animals_by_owner_id(id)
        if len(animals) == 0:
            return render_template('mypet.html', error=ERR_NOPOST), 400
        else:
            return render_template('mypet.html', id=get_username(),
                                   animals=animals), 200


@app.route('/mypet/update', methods=['GET', 'UPDATE', 'DELETE'])
@authentication_required
def update_mypet():
    if request.method == 'GET':
        id = get_db().get_user_id_by_id_session(session['id'])
        animals = get_db().get_animals_by_owner_id(id)
        return render_template('mypet_update.html', id=get_username(),
                               animals=animals)
    elif request.method == 'UPDATE':
        # get request data
        name = request.json['name']
        type = request.json['type']
        race = request.json['race']
        age = request.json['age']
        date = datetime.datetime.now().strftime('%Y-%m-%d')
        description = request.json['description']
        img_uri = request.json['img']

        if request_data_is_invalid(name=name, type=type, race=race, age=age,
                                   description=description):
            return jsonify({'success': False, 'error': ERR_FORM}), 400

        # front end send data_uri as data:image/base64,XXX
        # where xxx is the blob in string format
        listed_img_uri = img_uri.split(',')
        img_base64_tostring = listed_img_uri[1]

        # will not be updated if empty
        pic_id = ''
        user_id = get_db().get_user_id_by_id_session(session['id'])
        # the photo has been updated
        if len(img_base64_tostring) > 0:
            # TODO add image extention possibilities
            pic_id = get_username()
            get_db().update_pictures(pic_id, img_uri)

        get_db().update_animal(name, type, race, age, date, description,
                               pic_id, user_id)
        return_url = 'http://localhost:5000/mypet'
        return jsonify({'success': True, 'url': return_url}), 201

    elif request.method == 'DELETE':
        user_id = get_db().get_user_id_by_id_session(session['id'])
        pic_id = get_username()
        try:
            get_db().delete_animal(user_id, pic_id)
            return jsonify({'success': True, 'msg': INFO_DEL}), 201
        except Error:
            return jsonify({'success': False, 'error': ERR_SERVOR}), 500


def request_data_is_invalid(**kwargs):
    for key, value in kwargs.items():
        if value == '':
            return True
    return False


@app.route('/myaccount/', methods=['GET', 'UPDATE'])
@authentication_required
def get_myaccount():
    if request.method == 'GET':
        user_info = get_db().get_user_info_by_username(get_username())
        if user_info is None:
            return render_template('index.html', error=ERR_UNAUTH), 204
        else:
            return render_template('myaccount.html', id=get_username(),
                                   infos=user_info), 200
    elif request.method == 'UPDATE':
        # get request data
        username = request.json['username']
        name = request.json['name']
        family_name = request.json['family_name']
        phone = request.json['phone']
        address = request.json['address']
        password = request.json['password']

        if request_data_is_invalid(username=username, name=name,
                                   family_name=family_name, phone=phone,
                                   address=address,
                                   password=password):
            return jsonify({'success': False, 'error': ERR_FORM}), 400

        try:
            session_username = get_username()
            email = get_db().get_user_email_by_username(get_username())

            id = get_db().get_user_id_by_id_session(session['id'])
            salt = uuid.uuid4().hex
            hashed_password = hashlib.sha512(
                str(password + salt).encode('utf-8')).hexdigest()

            get_db().update_user(id, username, name, family_name, phone,
                                 address, email, salt, hashed_password,
                                 session_username)
            return_url = 'http://localhost:5000/myaccount'
            return jsonify({'success': True, 'url': return_url}), 201
        except IntegrityError:
            return jsonify({'success': False, 'error': ERR_UNI_USER}), 403


@app.route('/post', methods=['POST', 'GET'])
@authentication_required
def post():
    if request.method == 'POST':
        # get request data
        name = request.json['name']
        type = request.json['type']
        race = request.json['race']
        age = request.json['age']
        date = datetime.datetime.now().strftime('%Y-%m-%d')
        description = request.json['description']
        img_uri = request.json['img']

        if request_data_is_invalid(name=name, type=type, race=race,
                                   address=age, password=description):
            return jsonify({'success': False, 'error': ERR_FORM}), 400

        # to prevent collision
        user_id = get_db().get_user_id_by_id_session(session['id'])
        if user_has_already_posted(user_id):
            return jsonify({'success': False, 'error': ERR_UNI_POST}), 401
        else:
            pic_id = get_username()
            try:
                get_db().insert_pictures(pic_id, img_uri)
                # img_url = img_path

                get_db().insert_animal(name, type, race, age, date,
                                       description, pic_id, user_id)
                return_url = 'http://localhost:5000/mypet'
                return jsonify({'success': True, 'url': return_url}), 201
            except Error:
                return jsonify({'success': False, 'error': ERR_SERVOR}), 500

    elif request.method == 'GET':
        return render_template('user_post.html', id=get_username()), 200


def user_has_already_posted(user_id):
    animals = get_db().get_animals_by_owner_id(user_id)
    if len(animals) > 0:
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


@app.route('/api/animal_list', methods=['GET'])
def api_animal_list():
    animals = get_db().get_all_animals()
    if animals is None:
        return jsonify({'error': 'no animals'}), 204
    data = []
    for animal in animals:
        address = get_db().get_user_adresse_by_animal_id(animal[0])
        animal_dict = {'id': animal[0], 'name': animal[1], 'type': animal[2],
                       'race': animal[3], 'age': animal[4],
                       'date_creation': animal[5], 'description': animal[6],
                       'address': address}
        data.append(animal_dict)
    return jsonify(data), 200


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
    username = get_db().get_user_username_by_email(user_email)
    if username:
        token = generate_token()
        date = datetime.datetime.now().strftime('%Y-%m-%d')
        get_db().create_account(username, user_email, token, date)
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
        token = get_db().get_account_token_by_username(username)
        if token is None:
            redirect_url = 'http://localhost:5000/password_recovery/validate'
            return jsonify({'success': False, 'url': redirect_url,
                            'error': ERR_PASSWORD}), 401

        if password == token:
            # update user
            infos = get_db().get_user_info_by_username(username)
            user_id = infos[0]
            salt = uuid.uuid4().hex
            hashed_password = hashlib.sha512(
                str(token + salt).encode('utf-8')).hexdigest()
            get_db().update_user_password(user_id, salt, hashed_password)
            # delete account
            get_db().delete_account_by_username(username)
            # update session
            id_session = uuid.uuid4().hex
            get_db().save_session(id_session, username)
            session['id'] = id_session
            redirect_url = 'http://localhost:5000/myaccount'
            return jsonify({'success': True, 'url': redirect_url}), 201
        else:
            redirect_url = 'http://localhost:5000/password_recovery/validate'
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

    recipient = get_db().get_user_email_by_animal_id(animal_id)
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
    app.run()
