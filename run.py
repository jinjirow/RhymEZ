import sys, operator, rauth, ast

from flask import Flask, render_template, request, session, redirect, url_for
from nltk_webscrape import getSongs, getLyrics, parsePhonemes, colorGraphemes
from ss_params import CLIENT_ID, CLIENT_SECRET, BASE_URL, REDIRECT_URI, SECRET_KEY

sgs = []

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)
app.secret_key = SECRET_KEY
maps = { '0': 'ph' }

genius = rauth.OAuth2Service(
    client_id = CLIENT_ID,
    client_secret = CLIENT_SECRET,
    base_url = BASE_URL,
    authorize_url = BASE_URL + '/oauth/authorize',
    access_token_url = BASE_URL + '/oauth/token',
)

@app.route('/')
def renderInit(): # Session should only exist if the user has authenticated with Genius
    auth = True if(session) else False
    return render_template("index.html", auth=auth)

@app.route('/login', methods=['POST'])
def authorizeUser():
    params = {'redirect_uri': REDIRECT_URI,
              'response_type': 'code'}
    url = genius.get_authorize_url(**params)
    return redirect(url)

@app.route('/authorized')
def exchangeToken():
    if not 'code' in request.args:
        return redirect(url_for(renderInit))
    data = dict(code=request.args['code'], redirect_uri=REDIRECT_URI, grant_type='authorization_code')
    response = genius.get_raw_access_token(data=data, method='POST')
    parsed = ast.literal_eval(response.text)
    session['genius_token'] = parsed['access_token']
    return renderInit()

@app.route('/query', methods = ['POST'])
def querySongs():
    global sgs
    sgs = []
    authorizeUser()
    query = request.form['QueryBox']
    titles, urls = getSongs(query, session['genius_token'])
    sgs.append(titles)
    for i, url in enumerate(urls):
        maps[str(i + 1)] = str(url)
    return render_template("index.html", songs=titles, auth=True)


@app.route('/query/lyrics', methods = ['POST'])
def getPhones():
    sorted_list = []
    form = request.form['SongID'].split('-')
    selected = maps[form[0]]
    lyrics, phonemes = getLyrics(selected, session['genius_token'])
    stats = parsePhonemes(phonemes)
    text = colorGraphemes(phonemes, stats)
    for color in (sorted(stats.values(), key = operator.attrgetter('count'), reverse=True)):
        sorted_list.append(color)
    return render_template("index.html", lyrics = lyrics, songs = sgs[0], selected = form[1], phonemes = sorted_list, p_count = sorted_list.__len__(), auth=True)


if __name__ == "__main__":
    app.run()