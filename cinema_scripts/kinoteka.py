import re
from config import *
from flask import jsonify
from bs4 import BeautifulSoup
from db_utils import insert_movie, insert_cinema_locations, get_cinema_by_name
from models import Movie, CinemaLocation
from datetime import datetime, timedelta

def backup_kinoteka(session, cinema_data):
    """
    Backs up movie information from the Kinoteka cinema website.

    Args:
        session: Session object for making HTTP requests.
        cinema_data (dict): Information about the cinema.

    Returns:
        str: Success message if backup is successful, else error message.
    """
    cinema = get_cinema_by_name(cinema_data["name"])
    location = cinema_data['location']
    cinemaLocation = CinemaLocation(cinema[0], location['city'], location['city_code'], location['id'], location['name'], location['coord_latitude'], location['coord_longitude'])
    
    location_id = insert_cinema_locations(cinemaLocation)
        
    for x in range(DAYS_START_FROM_TODAY, DAYS_START_FROM_TODAY + DAYS_IN_ADVANCE + 1):
        date = datetime.now() + timedelta(days=x)
        date = date.strftime(DATE_MOVIE_SEARCH_FORMAT)

        try:
            return get_movies_from_kinoteka(session, cinema_data, cinema, location_id, date)
        except Exception as e:
            return jsonify(error=str(e)), 500  # Return error response

def get_movies_from_kinoteka(session, cinema_data, cinema, location_id, date):
    """
    Retrieves movie information from the Kinoteka cinema website for a specific date.

    Args:
        session: Session object for making HTTP requests.
        cinema_data (dict): Information about the cinema.
        cinema: Cinema details.
        location_id: ID of the cinema location.
        date (str): Date for which movies are to be retrieved.

    Returns:
        str: JSON response with movie information and date.
    """
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
    
    response = session.get(cinema_data["infoUrl"].format(date))

    soup = BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')
    movies = soup.find_all('article', class_='e-movie')

    for movie in movies:
        movie_urls.append(movie.find('a').get('href'))
        
    for url in movie_urls:
        response = session.get(url)
        soup = BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')
        
        #title
        title_tag = soup.find('h1', class_='p-movie-details__hero-title text-h5')
        if title_tag:
            title = title_tag.get_text()
        else:
            print("No title_tag found.")
        
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
        original_language_tag = soup.find('dt', text='Język oryginału:')
        if original_language_tag:
            original_language_tag_value = original_language_tag.find_next_sibling('dd')
            if original_language_tag_value:
                original_language = original_language_tag_value.get_text(strip=True)
            else:
                print("No original_language_tag_value found.")
        else:
            print("No original_language_tag found.")
            
        # language"
        language_tag = soup.find('dt', text='Wersja językowa:')
        if language_tag:
            language_tag_value = language_tag.find_next_sibling('dd')
            if language_tag_value:
                language = language_tag_value.get_text(strip=True)
            else:
                print("No language_tag_value found.")
        else:
            print("No language_tag found.")
            
        # subtitle"
        subtitle_tag = soup.find('dt', text='Napisy:')
        if subtitle_tag:
            subtitle_tag_value = subtitle_tag.find_next_sibling('dd')
            if subtitle_tag_value:
                subtitle = subtitle_tag_value.get_text(strip=True)
            else:
                print("No subtitle_tag_value found.")
        else:
            print("No subtitle_tag found.")
            
            
        # genre"
        genre_tag = soup.find('dt', text='Gatunek:')
        if genre_tag:
            genre_tag_value = genre_tag.find_next_sibling('dd')
            if genre_tag_value:
                genre = genre_tag_value.get_text(strip=True)
            else:
                print("No genre_tag_value found.")
        else:
            print("No genre_tag found.")
            
         # duration"
        duration_tag = soup.find('dt', text='Czas trwania filmu:')
        if duration_tag:
            duration_tag_value = duration_tag.find_next_sibling('dd')
            if duration_tag_value:
                duration = duration_tag_value.get_text(strip=True)
                duration = int(re.search(r'\d+', duration).group())
            else:
                print("No duration_tag_value found.")
        else:
            print("No duration_tag found.")
            
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
        data = str({
        "greeting": movie_urls
    })), 200