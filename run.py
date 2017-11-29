import sys, operator

from flask import Flask, render_template, request
from nltk_webscrape import getSongs, getLyrics, parsePhonemes, colorGraphemes

sgs = []

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)

maps = { '0': 'ph' }


@app.route('/')
def renderSongs():
    return render_template("index.html")


@app.route('/query', methods = ['POST'])
def querySongs():
    global sgs
    sgs = []
    query = request.form['QueryBox']
    titles, urls = getSongs(query)
    sgs.append(titles)
    for i, url in enumerate(urls):
        maps[str(i + 1)] = str(url)
    return render_template("index.html", songs=titles)


@app.route('/query/lyrics', methods = ['POST'])
def getPhones():
    sorted_list = []
    form = request.form['SongID'].split('-')
    selected = maps[form[0]]
    lyrics, phonemes = getLyrics(selected)
    stats = parsePhonemes(phonemes)
    text = colorGraphemes(phonemes, stats)
    for color in (sorted(stats.values(), key = operator.attrgetter('count'), reverse=True)):
        sorted_list.append(color)
    return render_template("index.html", lyrics = lyrics, songs = sgs[0], selected = form[1], phonemes = sorted_list, p_count = sorted_list.__len__())


if __name__ == "__main__":
    app.run()