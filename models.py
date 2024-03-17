# models.py
class CinemaLocation:
    def __init__(self, cinema_id, city, city_code, location_id, name, coord_latitude, coord_longitude):
        self.cinema_id = cinema_id
        self.city = city
        self.city_code = city_code
        self.location_id = location_id
        self.name = name
        self.coord_latitude = coord_latitude
        self.coord_longitude = coord_longitude
        
class Movie:
    def __init__(self, title, description, duration, original_lang, genre, classification, release_year, trailer_url, poster_url):
        self.title = title
        self.description = description
        self.duration = duration
        self.original_lang = original_lang
        self.genre = genre
        self.classification = classification
        self.release_year = release_year
        self.trailer_url = trailer_url
        self.poster_url = poster_url

class MoviesInCinema:
    def __init__(self, movie_id, cinema_id, location_id, day_title, cinema_movie_url, language):
        self.movie_id = movie_id
        self.cinema_id = cinema_id
        self.location_id = location_id
        self.day_title = day_title
        self.cinema_movie_url = cinema_movie_url
        self.language = language
