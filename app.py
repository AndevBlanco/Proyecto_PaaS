from flask import Flask, render_template, session, abort, redirect, request, url_for
import database, os, pathlib, requests, json
from dotenv import load_dotenv
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests

load_dotenv()

app = Flask(__name__)
app.secret_key = "your-secret-key"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_credentials.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
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
        'my_games': [],
        'games': []
    }
    game_list_db = database.db.games.find()
    for i in game_list_db:
        if(i['winner_name'] == ''):
                i['winner_name'] = 'Pendiente'

        if(i['user_uuid'] == session['google_id']):
            game_list['my_games'].append(i)
        else:
            game_list['games'].append(i)

    print(game_list)

    return render_template('home.html', games_list=game_list)


@app.route('/login', methods=['POST'])
def login():
    authorization_url, state = flow.authorization_url()
    print(state)
    session["state"] = state
    return redirect(authorization_url)

@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)
    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )
    session['google_id'] = id_info.get("sub")
    session['name'] = id_info.get("name")
    user_exist = database.db.users.find_one({"uuid": session['google_id']})
    if(not user_exist):
        database.db.users.insert_one({"uuid": session['google_id'], "name": session['name']})
    print(session['google_id'])
    return redirect("/home")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/protected_area")
def protected_area():
    print(session)
    return f"Hello {session['name']}! <br/> <a href='/logout'><button>Logout</button></a>"

@app.route("/test")
def test():
    print(os.getenv("DB_URI"))
    database.db.collection.insert_one({"name": "John"})
    return "Connected to the data base!"

def logout():
    session.clear()

@app.route("/create")
def create():
    print(session)
    return render_template("create.html")

@app.route("/create", methods=['POST'])
def save_game():
    obj = json.loads('[{}]'.format(request.form['caches']))
    for i in range(0, len(obj)):
        obj[i]['clue'] = request.form['clue' + str(i)]

    database.db.games.insert_one({"user_uuid": session['google_id'], "user_name": session['name'], "name": request.form['game_name'], "north": request.form['north'], "south": request.form['south'], "east": request.form['east'], "west": request.form['west'], "caches": obj, "number_caches": len(obj), "winner_name": "", "active": True})
    return render_template("create.html")

