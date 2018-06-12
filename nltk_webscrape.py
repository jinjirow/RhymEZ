import requests
import pronouncing
import random
import re
import math
from bs4 import BeautifulSoup
from ss_params import BASE_URL
from collections import defaultdict


verse_list = []

COUNTER = 0

class P_Color:
    def __init__(self, color, sound):
        global COUNTER
        self.count = 1
        self.color = color
        self.sound = sound
        self.id = COUNTER
        COUNTER += 1
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

"""
Takes all the words and maps the phonemes for each word
:return:
"""
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
                except Exception as ex:
                    # Could not parse word? Should be fixed
                    continue
    #print(color_mappings)
    return color_mappings

def song_diff(song_1, song_2):
    ph_1 = set(song_1.keys())
    ph_2 = set(song_2.keys())

    similar = ph_1.intersection(ph_2)
    difference = (ph_1.difference(ph_2)).union(ph_2.difference(ph_1))

    count = 0
    for key in similar:
        #count += abs((song_1[key].count - song_2[key].count))
        count += abs((song_1[key].count - song_2[key].count)/float(min(song_1[key].count, song_2[key].count)))

    metric = (float(count) + 1)/(float(len(similar)) + 1)
    metric = metric * (len(difference) + 1)

    return metric

def song_diff2(song_1, song_2):
    ph_1 = set(song_1.keys())
    ph_2 = set(song_2.keys())

    similar = ph_1.intersection(ph_2)
    difference = (ph_1.difference(ph_2)).union(ph_2.difference(ph_1))

    count = 1
    for key in similar:
        print "Song1 Key: ", str(song_1[key].count)
        print "Song2 Key: ", str(song_2[key].count)
        count += (song_1[key].count - song_2[key].count + 1.0)/float((song_1[key].count + song_2[key].count))

    #metric = (float(count) + 1)/(float(len(similar)) + 1)

    print len(difference)
    metric = count * (len(difference)/(math.log(float(len(ph_1) + len(ph_2))))+1.0)

    return metric

def colorGraphemes(phonemes, sts): # Trivial way to display all mapped colors using just their pronunciations
    final_div = ''
    for verse in phonemes:
        for line in verse:
            for word in line:
                sp = word.split('-*-')
                try:
                    test = sp[1].split(' ')
                    for sound in sp[1].split(' '):
                        if not sound == '':
                            color = sts[re.sub('\d', '', sound)].color
                            cs = re.sub('\d', '', sound)
                            final_div += "<span class='" + cs + "'style='background-color:" + color + "'>" + sound + "</span>"
                            print('')
                except Exception as e:
                    #print(type(e))
                    final_div += '<span>' + word.split(' ')[0] + '</span>' # Word wasn't parsed correctly (no pronunciation)
                final_div += '  '
            final_div += '<br/>'
        final_div += '<br/><br/>'
    return final_div

def find_rhymes(lyrics):
    regex = re.compile(r'[^a-zA-Z]')
    rhyme_dict = defaultdict(list)
    for word in lyrics:
        word = regex.sub('', word) # make every word only alphabetical
        for phone in pronouncing.phones_for_word(word):
            rhyme_dict[tuple(phone.split()[-2:])].append(word)
    return rhyme_dict
