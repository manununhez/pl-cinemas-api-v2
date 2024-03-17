import requests
import re
from datetime import date
from flask import Flask,jsonify
from bs4 import BeautifulSoup
from db_utils import insert_movie, insert_cinema_locations, get_cinema_by_name, cleanTables
from models import Movie, CinemaLocation
from datetime import datetime, timedelta

app = Flask(__name__)

HTTP_CLIENT_TIMEOUT = 60
DAYS_IN_ADVANCE = 2
TIMEZONE = "Europe/Warsaw"
DAYS_START_FROM_TODAY = 0
DAYS_START_FROM_TOMORROW = 1
DATE_MOVIE_SEARCH_FORMAT = '%Y-%m-%d'
    
KINOTEKA_DATA = {
    "id" : 35,
    "city" : "Warszawa",
    "city_code" : "warszawa",
    "location" : "Warszawa",
    "name": "Warszawa",
    "coord_latitude" : "52.231816",
    "coord_longitude" : "21.005839"
}
KINOTEKA = "Kinoteka"
KINOTEKA_URL_FORMAT = 'https://kinoteka.pl/repertuar/?date={}'


@app.route("/backup-kinoteka")
def backupKinoteka():
    cleanTables()
    
    cinema = get_cinema_by_name(KINOTEKA)
    cinemaLocation = CinemaLocation(cinema[0], KINOTEKA_DATA['city'], KINOTEKA_DATA['city_code'], KINOTEKA_DATA['id'], KINOTEKA_DATA['name'], KINOTEKA_DATA['coord_latitude'], KINOTEKA_DATA['coord_longitude'])
    
    location_id = insert_cinema_locations(cinemaLocation)
        
    for x in range(DAYS_START_FROM_TODAY, DAYS_START_FROM_TODAY + DAYS_IN_ADVANCE + 1):
        date = datetime.now() + timedelta(days=x)
        date = date.strftime(DATE_MOVIE_SEARCH_FORMAT)

        try:
            result = getMoviesFromKinoteka(cinema, location_id, date)
        except Exception as e:
            return f"{type(e).__name__}: {e}"

    return "Success!"

def getMoviesFromKinoteka(cinema, location_id, date):
    title = ""
    description = ""
    duration = ""
    original_language = ""
    genre = ""
    release_year = ""
    classification = ""
    trailer_url = ""
    poster_url = ""
    language = ""
    movie_urls = []
    
    response = requests.get(KINOTEKA_URL_FORMAT.format(date))

    soup = BeautifulSoup(response.content, 'html.parser')
    movies = soup.find_all('article', class_='e-movie')

    for movie in movies:
        movie_urls.append(movie.find('a').get('href'))
        
    for url in movie_urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        #title
        title_tag = soup.find('h1', class_='p-movie-details__hero-title text-h5')
        if title_tag:
            title = title_tag.get_text()
        else:
            print("No title tag found.")
        
        # poster
        poster_tag = soup.find('picture', class_='p-movie-details__hero-poster')
        if poster_tag:
            poster_url = poster_tag.find('img')['src']
        else:
            print("No poster_tag found.")
            
        # trailer
        trailer_tag = soup.find('iframe')
        if trailer_tag:
            trailer_url = trailer_tag['src']
        else:
            print("No trailer_tag found.")
        
        # original_language"
        dt_tag = soup.find('dt', text='Język oryginału:')
        if dt_tag:
            dd_tag = dt_tag.find_next_sibling('dd')
            if dd_tag:
                original_language = dd_tag.get_text(strip=True)
            else:
                print("No corresponding <dd> tag found.")
        else:
            print("No <dt> tag with text 'Język oryginału:' found.")
            
        # language"
        dt_tag = soup.find('dt', text='Wersja językowa:')
        if dt_tag:
            dd_tag = dt_tag.find_next_sibling('dd')
            if dd_tag:
                language = dd_tag.get_text(strip=True)
            else:
                print("No corresponding <dd> tag found.")
        else:
            print("No <dt> tag with text 'Wersja językowa:' found.")
            
        # subtitle"
        dt_tag = soup.find('dt', text='Napisy:')
        if dt_tag:
            dd_tag = dt_tag.find_next_sibling('dd')
            if dd_tag:
                subtitle = dd_tag.get_text(strip=True)
            else:
                print("No corresponding <dd> tag found.")
        else:
            print("No <dt> tag with text ''Napisy:' found.")
            
            
        # genre"
        dt_tag = soup.find('dt', text='Gatunek:')
        if dt_tag:
            dd_tag = dt_tag.find_next_sibling('dd')
            if dd_tag:
                genre = dd_tag.get_text(strip=True)
            else:
                print("No corresponding <dd> tag found.")
        else:
            print("No <dt> tag with text 'Gatunek:' found.")
            
         # duration"
        dt_tag = soup.find('dt', text='Czas trwania filmu:')
        if dt_tag:
            dd_tag = dt_tag.find_next_sibling('dd')
            if dd_tag:
                duration = dd_tag.get_text(strip=True)
                duration = int(re.search(r'\d+', duration).group())
            else:
                print("No corresponding <dd> tag found.")
        else:
            print("No <dt> tag with text 'Czas trwania filmu:' found.")
            
        #description
        description_tag = soup.find('div', class_='mce-content-body text-body-small')

        if description_tag:
            description_p = description_tag.find_all('p')
            
            description = ' '.join(p.get_text(strip=True) for p in description_p)
        else:
            print("No description content found.")
        
        movie = Movie(title, description, duration, original_language, genre, classification, release_year, trailer_url, poster_url)
        
        insert_movie(cinema[0], location_id, url, movie, date, language)
        
    
    return jsonify(
        greeting = movie_urls,
        date = date.today(),
    )

@app.route("/multikino")
def multikino():
    url = 'https://multikino.pl/repertuar/bydgoszcz?data={}'

    response = requests.get(url)

    soup = BeautifulSoup(response.content, 'html.parser')
    movies = soup.find_all('div', class_='filmlist')
    print(movies)

    urls = []
    for movie in movies:
        urls.append(movie.find('a').get('href'))
    
    return jsonify(
        greeting=urls,
        date=date.today(),
    )


@app.route("/itau")
def itau():
    url = 'http://cines.com.py/cine/2--Cines%20Ita%C3%BA%20del%20Sol'
    response = requests.get(url)

    soup = BeautifulSoup(response.content, 'html.parser')
    frames = soup.find_all('div', class_='cartelera_cuadro')
    movies = soup.find_all('div', class_='texto_cartelera')
    # print(frames)

    base_url = 'http://cines.com.py'  # Base URL to complete relative URLs

    titles = []
    original_titles = []
    movie_urls = []
    poster_urls = []

    for frame in frames:
        # Check if the <a> tag exists within the <div class="cartelera_cuadro">
        if frame.find('div', class_='texto_cartelera'):
            href = frame.find('a')['href']
            # Complete the URL manually by concatenating the base URL with the relative URL
            complete_url = base_url + href.replace(" ", "%20")
            movie_urls.append(complete_url)

            src = frame.find('img')['src']
            poster_urls.append(base_url + src)


    for movie in movies:
        text = movie.find('h1').get_text().strip()
        matches = re.match(r'^(.*?)\s*\((.*?)\)\s*$', text)
        if matches:
            title = matches.group(1).strip()
            original_title = matches.group(2).strip()
            titles.append(title)
            original_titles.append(original_title)
        else:
            # If the title doesn't follow the pattern, consider it as both title and original title
            titles.append(text)
            original_titles.append(text)
    
    return jsonify(
        titles = titles,
        original_titles = original_titles,
        movie_urls = movie_urls,
        poster_urls = poster_urls,
        date = date.today(),
    )


# https://www.cinemark.com.py/peliculas?tag=2900 #Cinemark Asuncion
# https://www.cinemark.com.py/peliculas?tag=2901 #Cinemark CDE