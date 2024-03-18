import re
from bs4 import BeautifulSoup
from flask import jsonify
from datetime import date

def itau(session):
    url = 'http://cines.com.py/cine/2--Cines%20Ita%C3%BA%20del%20Sol'
    response = session.get(url)

    soup = BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')
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