# RhymEZ

An experiment in natural language processing and lyrics.

### Dependencies

Flask, BeautifulSoup, RAuth, Pronouncing

### Usage

```
python run.py
```

*for the sake of readability/security I'm storing serveral parameters in an external python file with the following structure*

```
CLIENT_ID = YOUR_CLIENT_ID

CLIENT_SECRET = YOUR_CLIENT_SECRET

BASE_URL = 'https://api.genius.com'

REDIRECT_URI = URL_FOR_CALLBACK

SECRET_KEY = SECRET_KEY (used for flask session management)
```
