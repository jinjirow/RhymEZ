# Phoneme detection using 'pronouncing' library.
import requests
import pronouncing
from bs4 import BeautifulSoup
import random, re
from ss_params import BASE_URL
from collections import defaultdict


verse_list = []

class P_Color:
    def __init__(self, color, sound):
        self.count = 1
        self.color = color
        self.sound = sound
    def increment(self):
        self.count += 1


# API Requests

def getLyrics(path, TOKEN): # Scrape Genius website for lyrics. Followed this example from: https://bigishdata.com/2016/09/27/getting-song-lyrics-from-geniuss-api-scraping/
    headers = {'Authorization': 'Bearer ' + TOKEN}
    song_url = BASE_URL + path
    response = requests.get(song_url, headers=headers)
    json = response.json()
    path = json["response"]["song"]["path"]
    page_url = "http://genius.com" + path
    page = requests.get(page_url)
    html = BeautifulSoup(page.text, "html.parser")
    verses = html.find('div', class_='lyrics').get_text().encode('utf-8')
    return verses, findPhonemes(verses.split("\n\n"))

def getAccountInfo(TOKEN):
    headers = {'Authorization': 'Bearer ' + TOKEN}
    search_url = BASE_URL + "/account"
    response = requests.get(search_url, headers=headers)
    parsed = response.json()
    account = parsed['response']['user']
    return account['header_image_url'].encode('utf-8'), account['name'].encode('utf-8')

def getSongs(query, TOKEN): # Returns a list of song titles and their respective api_paths
    titles, urls = [], []
    headers = {'Authorization': 'Bearer ' + TOKEN}
    search_url = BASE_URL + "/search"
    song_title = query
    params = {'q': song_title}
    response = requests.get(search_url, params=params, headers=headers)
    json = response.json()
    for hit in json["response"]["hits"]:
        titles.append(str((hit["result"]["full_title"]).encode('utf-8')))
        urls.append((hit["result"]["api_path"]))
    return titles, urls

def findPhonemes(lyrics):
    phonemes = []
    hc, oc = 0, 0
    for verse in lyrics:
        vl = []
        if not(verse == ''):
            test = verse.split('\n')
            for line in verse.split('\n'):
                wfl = []
                for word in line.split(' '):
                    phones = pronouncing.phones_for_word(re.sub('[^0-9a-zA-Z]+', '', word.lower())) # returns CMU Pronouncing dictionary phonemes for each word
                    #syllables = str(pronouncing.syllable_count(str(phones[0])))
                    tagged = (word  + ' -*- ' + str(phones[0].encode('utf-8')) if (phones.__len__() > 0) else (word + ' (???)'))
                    oc += 1
                    hc += 1 if(phones.__len__() > 0) else 0
                    wfl.append(tagged)
                vl.append(wfl)
        phonemes.append(vl)
    #accuracy = float(hc)/float(oc)
    return phonemes


def parsePhonemes(ph):
    color_mappings = {}
    r = lambda: random.randint(0, 255)
    for verse in ph:
        for line in verse:
            for word in line:
                sounds = word.split('-*-')
                try:
                    sds = sounds[1].replace(')', '').split(' ')
                    for sound in sds:
                        if not sound == '':
                            candidate = re.sub('\d', '', sound)
                            if candidate not in color_mappings:
                                new_color = P_Color('#%02X%02X%02X' % (r(), r(), r()), candidate) # Generate random RGB value for every unique sound/phoneme.
                                color_mappings[candidate] = new_color
                            else:
                                color_mappings[candidate].count += 1
                except:
                    # Could not parse word? Should be fixed
                    print('')
    return color_mappings

def colorGraphemes(phonemes, sts):
    final_div = ''
    for verse in phonemes:
        for line in verse:
            for word in line:
                lines, linesum = '', ''
                colors = []
                sp = word.split('-*-')
                lines += ' ' + str(sp[0])
                try:
                    for sound in sp[1].split(' '):
                        if not sound == '':
                            candidate = re.sub('\d', '', sound)
                            color = str(sts[candidate].color)
                            linesum += ("<span style='color: " + color + "'>-</span>   ")
                except:
                    print('?')
            final_div += '\n'
        final_div += '\n\n'
    return

def find_rhymes(lyrics):
    regex = re.compile(r'[^a-zA-Z]')
    rhyme_dict = defaultdict(list)
    for word in lyrics:
        word = regex.sub('', word) # make every word only alphabetical
        for phone in pronouncing.phones_for_word(word):
            rhyme_dict[tuple(phone.split()[-2:])].append(word)
    return rhyme_dict
