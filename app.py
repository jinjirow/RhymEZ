import sys
import operator
import rauth
import ast
import sqlite3 as sql

from flask import Flask, render_template, request, session, redirect, url_for
from nltk_webscrape import getSongs, getLyrics, parsePhonemes, getAccountInfo, colorGraphemes, song_diff, song_diff2
from ss_params import CLIENT_ID, CLIENT_SECRET, BASE_URL, REDIRECT_URI, SECRET_KEY


# Set default text encoding
reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Global 'Session' variables
maps = { '0': 'ph' }
SONGS = []
SEARCHED = []
QUERY = ''
TITLES = None
LYRICS = None
SONGS = None
P_COUNT = None
PD = None
SELECTED = None
PHONEMES = None
COMPARE = []

# Genius Authentication Flow

genius = rauth.OAuth2Service(
    client_id = CLIENT_ID,
    client_secret = CLIENT_SECRET,
    base_url = BASE_URL,
    authorize_url = BASE_URL + '/oauth/authorize',
    access_token_url = BASE_URL + '/oauth/token',
)


@app.route('/')
def renderInit():
    # Session should only exist if the user has authenticated with Genius
    if(session):
        auth, acc, name = True, session['avatar_url'], session['name']
    else:
        auth, acc, name = False, '', ''
    if not SELECTED == None:
        return render_template("results.html", auth=auth, url=acc, name=name, lyrics=LYRICS,
            selected=SELECTED, songs=SONGS[0], p_count=P_COUNT, pd=PD, query=QUERY, phonemes=PHONEMES)
    else:
        return render_template("index.html", auth=auth, url=acc, name=name)


@app.route('/upload')
def uploadPage():
    return render_template("upload.html", auth=True)

def saveNewLyric(title, auth, ltype, genre, lyric, highlight, phoneme, count):
    ph = "placeholder"
    con = sql.connect("phscrape.db")
    cur = con.cursor()
    query = "INSERT INTO results (title,author,type,genre,lyrics,highlighted,phonemes,count) VALUES (?,?,?,?,?,?,?,?)"
    cur.execute(query, (title, auth, ltype, genre, lyric, highlight, ph, count))
    con.commit()
    con.close()


@app.route('/upload/submit', methods=['POST'])
def submitLyric():
    title = request.form['inputTitle']
    auth = request.form['inputArtist']
    ltype = request.form['typeSelect']
    genre = request.form['inputGenre']
    lyric = request.form['inputLyric']
    highlight = "test_highlight2"
    phoneme = "test_phoneme2"
    count = "test_count2"
    saveNewLyric(title, auth, ltype, genre, lyric, highlight, phoneme, count)
    return render_template("upload.html", auth=True)


@app.route('/lyrics')
def lyricPage():
    con = sql.connect("phscrape.db")
    cur = con.cursor()
    cur.execute("select * from results")
    rows = cur.fetchall()
    con.close()
    if not SELECTED == None:
        return render_template("lyrics.html", auth=True, lyrics=LYRICS,
            selected=SELECTED, songs=SONGS[0], p_count=P_COUNT, pd=PD, query=QUERY, phonemes=PHONEMES)
    else:
        return render_template("lyrics.html", auth=True)


@app.route('/login', methods=['POST'])
def authorizeUser():
    params = {'redirect_uri': REDIRECT_URI,
              'scope' : 'me',
              'response_type': 'code'}
    url = genius.get_authorize_url(**params)
    return redirect(url)


@app.route('/authorized')
def exchangeToken():
    if not 'code' in request.args:
        return renderInit()
    data = dict(code=request.args['code'], redirect_uri=REDIRECT_URI, grant_type='authorization_code')
    response = genius.get_raw_access_token(data=data, method='POST')
    parsed = ast.literal_eval(response.text)
    session['genius_token'] = parsed['access_token']
    session['avatar_url'], session['name'] = getAccountInfo(parsed['access_token'])
    return renderInit()



@app.route('/query', methods = ['POST'])
def querySongs():
    global QUERY, TITLES, SONGS
    if not (session):
        return redirect(url_for(renderInit))
    SONGS = []
    authorizeUser()
    query = request.form['QueryBox']
    titles, urls = getSongs(query, session['genius_token'])
    SONGS.append(titles)
    for i, url in enumerate(urls):
        maps[str(i + 1)] = str(url)
    QUERY = query
    TITLES = titles
    if not SELECTED == None:
        return render_template("results.html", query=QUERY, songs=TITLES, auth=True, acc=session['avatar_url'],
            selected=SELECTED, p_count=P_COUNT, pd=PD, phonemes=PHONEMES, lyrics=LYRICS)
    else:
        return render_template("index.html", query=QUERY, songs=TITLES, auth=True, acc=session['avatar_url'])


@app.route('/query/lyrics', methods = ['POST'])
def getPhones():
    global SONGS, P_COUNT, PD, SELECTED, LYRICS, PHONEMES, COMPARE
    if not (session):
        return redirect(url_for(renderInit))
    sorted_list = []
    form = request.form['SongID'].split('-')
    selected = maps[form[0]]
    lyrics, phonemes = getLyrics(selected, session['genius_token'])
    stats = parsePhonemes(phonemes)
    pronouncing_div = colorGraphemes(phonemes, stats)
    for color in (sorted(stats.values(), key = operator.attrgetter('count'), reverse=True)):
        sorted_list.append(color)
    PHONEMES = sorted_list
    LYRICS = lyrics
    SELECTED = form[1]
    PD = pronouncing_div
    P_COUNT = sorted_list.__len__()
    COMPARE.append(stats)

    if (COMPARE.__len__() > 1):
        diff_test = song_diff(COMPARE[0], COMPARE[1])
        diff_test2 = song_diff2(COMPARE[0], COMPARE[1])
    return render_template("results.html", lyrics = lyrics, songs = SONGS[0], selected = form[1],
                           phonemes=sorted_list, p_count=sorted_list.__len__(), auth=True,
                           acc=session['avatar_url'], pd=pronouncing_div, query=QUERY)

@app.route('/query/lyrics/save', methods = ['POST', 'GET'])
def saveLyric():
    global sorted_list, lyrics, pronouncing_div
    sp = SELECTED.encode('utf-8').split("by")
    title = sp[0]
    author = sp[1]
    ltype = "Song"
    genre = "Placeholder"
    lyric = LYRICS
    highlight = PD
    phoneme = PHONEMES
    count = P_COUNT
    saveNewLyric(title, author, ltype, genre, lyric, highlight, phoneme, count)
    return render_template("results.html", lyrics = lyrics, songs = SONGS[0], selected = SELECTED,
                       phonemes=sorted_list, p_count=sorted_list.__len__(), auth=True,
                       pd=pronouncing_div, query=QUERY)


if __name__ == "__main__":
    app.run()
