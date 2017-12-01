from pronouncing import phones_for_word
from collections import defaultdict
import re

regex = re.compile(r'[^a-zA-Z]')
rhyme_dict = defaultdict(list)

def add_word(word):
    word = regex.sub('', word)
    for phone in phones_for_word(word):
        rhyme_dict[tuple(phone.split()[-2:])].append(word)


if __name__ == "__main__":
    while True:
        w = raw_input("input word: ")
        add_word(w)
        print "WOrds that rhyme with it: "
        print rhyme_dict[tuple(phones_for_word(w)[0].split()[-2:])]
