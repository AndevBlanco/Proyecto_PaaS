from flask import Flask, render_template, session, abort, redirect, request, url_for
import database
import os
import pathlib
import requests
import json
from dotenv import load_dotenv
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)
app.secret_key = "your-secret-key"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
UPLOAD_FOLDER = '\\static\\img'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
client_secrets_file = os.path.join(pathlib.Path(
    __file__).parent, "client_credentials.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:8500/callback"
)


client = os.getenv("DB_URI")


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/home')
@login_is_required
def home():
    game_list = {
        'user_name': session['name'],
        'my_games': [],
        'games': []
    }
    game_list_db = database.db.games.find()
    for i in game_list_db:
        i['active_users'] = len(i['players']) if 'players' in i else 0
        if (i['winner_name'] == ''):
            i['winner_name'] = 'Pendiente'

        if (i['user_uuid'] == session['google_id']):
            game_list['my_games'].append(i)
        else:
            game_list['games'].append(i)


    return render_template('home.html', games_list=game_list)


@app.route('/login', methods=['POST'])
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(
        session=cached_session)
    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )
    session['google_id'] = id_info.get("sub")
    session['name'] = id_info.get("name")
    user_exist = database.db.users.find_one({"uuid": session['google_id']})
    if (not user_exist):
        database.db.users.insert_one(
            {"uuid": session['google_id'], "name": session['name']})
    return redirect("/home")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/protected_area")
def protected_area():
    return f"Hello {session['name']}! <br/> <a href='/logout'><button>Logout</button></a>"


@app.route("/test")
def test():
    database.db.collection.insert_one({"name": "John"})
    return "Connected to the data base!"


def logout():
    session.clear()


@app.route("/create")
def create():
    return render_template("create.html")


@app.route("/create", methods=['POST'])
def save_game():
    obj = json.loads('[{}]'.format(request.form['caches']))
    for i in range(0, len(obj)):
        obj[i]['clue'] = request.form['clue' + str(i)]
        obj[i]['found'] = False
        obj[i]['user_name_find'] = ''
        obj[i]['user_uuid_find'] = ''
        obj[i]['image'] = request.files['image' + str(i)].filename
        if obj[i]['image'] != '':
            f = request.files['image' + str(i)]
            f.save(f.filename)
            os.rename(os.path.abspath(f.filename), os.path.abspath(".")+'/static/img/' + f.filename)

    database.db.games.insert_one({"user_uuid": session['google_id'], "user_name": session['name'], "name": request.form['game_name'], "north": request.form['north'],
                                 "south": request.form['south'], "east": request.form['east'], "west": request.form['west'], "caches": obj, "number_caches": len(obj), "number_caches_found": 0, "number_caches_left": len(obj), "winner_name": "", "players": [], "active": True})
    return render_template("create.html")


@app.route("/play")
def play():
    game_id = request.args.get('game')
    if(game_id):
        game_data_db = database.db.games.find_one({"_id": ObjectId(game_id)})

        if(game_data_db['winner_name'] == session['name']):
            game_data_db['winner_you'] = '¡Enhorabuena {}, eres el ganador del juego! \n ¡Vaya pedazo de crack!'.format(session['name'])
    
    return render_template("play.html", game_data=game_data_db)

@app.route("/play", methods=["POST"])
def save_play():
    if (request.method == "POST"):
        cache = int(request.form['cache'])
        game_id = request.form['id_play']
        game_data_db = database.db.games.find_one({"_id": ObjectId(game_id)})
        if(game_data_db['caches'][cache]['found'] == False):
            game_data_db['caches'][cache]['user_uuid_find'] = session['google_id']
            game_data_db['caches'][cache]['user_name_find'] = session['name']
            game_data_db['caches'][cache]['found'] = True
            game_data_db['number_caches_found'] = game_data_db['number_caches_found'] + 1
            game_data_db['number_caches_left'] = game_data_db['number_caches_left'] - 1
            band = False
            user_position = 0
            count = 0
            for i in game_data_db['players']:
                if(i['player_name'] == session['name']):
                    user_position = count
                    i['found'] += 1
                    band = True

                count += 1
            
            if(band != True):
                game_data_db['players'].append({'player_name': session['name'], 'found':  1})
                user_position = len(game_data_db['players']) - 1
            
            if(game_data_db['number_caches_found'] == game_data_db['number_caches'] and game_data_db['number_caches_left'] == 0 and game_data_db['number_caches'] == game_data_db['players'][user_position]['found']):
                game_data_db['winner_name'] = session['name']
                game_data_db['active'] = False


    database.db.games.update_one({"_id": ObjectId(game_id)}, {"$set": game_data_db})

    # return render_template("play.html", game_data=game_data_db)
    # return redirect(request.url)
    return redirect(url_for("play", game=game_id))


@app.route("/game")
def game():
    game_id = request.args.get('game')
    game_data_db = database.db.games.find_one({"_id": ObjectId(game_id)})

    return render_template("game.html", game_data=game_data_db)


@app.route("/game", methods=["POST"])
def restart():
    if (request.method == "POST"):
        game_id = request.args.get('game')
        game_data_db = database.db.games.find_one({"_id": ObjectId(game_id)})
        game_data_db['number_caches_found'] = 0
        game_data_db['number_caches_left'] = game_data_db['number_caches']
        game_data_db['winner_name'] = ''
        game_data_db['active'] = True
        game_data_db['players'] = []
        for i in game_data_db['caches']:
            i['user_name_find'] = ''
            i['user_uuid_find'] = ''
            i['found'] = False
            
        database.db.games.update_one({"_id": ObjectId(game_id)}, {"$set": game_data_db})

    return redirect("/home")