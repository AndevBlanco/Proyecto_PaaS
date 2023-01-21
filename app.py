from flask import Flask, render_template, session, abort, redirect, request
import database, os, pathlib, requests
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

@app.route('/')
def index():
    print(os.getenv("GOOGLE_CLIENT_ID"))
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    authorization_url, state = flow.authorization_url()
    print(state)
    session["state"] = state
    return redirect(authorization_url)

@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)
    if not session["state"] == request.args["state"]:
        abort(500) 
    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)
    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )
    session['goole_id'] = id_info.get("sub")
    session['name'] = id_info.get("name")
    return redirect("/protected_area")

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