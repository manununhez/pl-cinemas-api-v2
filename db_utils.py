# db_utils.py
import psycopg2
import os

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database=os.environ['DB_NAME'],
            user=os.environ['DB_USERNAME'],
            password=os.environ['DB_PASSWORD']
        )
        return conn
    except psycopg2.Error as e:
        print("Error:", e)
        return None

def get_cinema_by_name(cinema_name):
    """Retrieves cinema information by name."""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM cinemas WHERE name = %s limit 1", (cinema_name,))
            row = cur.fetchone()
            cur.close()
            conn.close()
            return row
        except psycopg2.Error as e:
            print("Error:", e)
            return None
    return None

# Cinema locations
def insert_cinema_locations(cinema_location):
    """Inserts cinema locations into the database."""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
    
            cinema_location_id = get_cinema_by_location(cur, cinema_location.location_id)

            if not cinema_location_id:  # if the location does not exist
                cur.execute('INSERT INTO cinema_locations (cinema_id, city, city_code, location_id, name, coord_latitude, coord_longitude)'
                            'VALUES (%s, %s, %s, %s, %s, %s, %s)',
                            (cinema_location.cinema_id, cinema_location.city, cinema_location.city_code, cinema_location.location_id, cinema_location.name, cinema_location.coord_latitude, cinema_location.coord_longitude))
                conn.commit()
            
                cinema_location_id = cur.fetchone()[0]  # Return new inserted id
            
            cur.close()
            conn.close()
            
            return cinema_location_id
        except psycopg2.Error as e:
            print("Error:", e)
        return None
    return None


    
def get_cinema_by_location(cur, location):
    """Retrieves cinema by location."""
    try:
        cur.execute("SELECT id FROM cinema_locations WHERE location_id = %s", (str(location),))
        row = cur.fetchone()
        if row:
            return row[0]
        return None
    except psycopg2.Error as e:
        print("Error:", e)
        return None

# Movies
def insert_movie(cinema_id, location_id, link_cinema_movie_page, movie_to_insert, date, language):
    """Inserts a movie into the database."""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()

            movie_id = get_movie_id_by_title(cur, movie_to_insert.title)
            
            if not movie_id:  # if the movie does not exist
                # first create the new movie and get the inserted ID
                # then associate the movie with the cinema
                print("Inserting new movie")
                movie_id = insert_new_movie(conn, cur, movie_to_insert)

                if movie_id:
                    insert_movies_in_cinema(conn, cur, movie_id, cinema_id, location_id, date, link_cinema_movie_page, language)

            else:
                print("Updating new movie")

                # if the movie already exists
                update_movie(conn, cur, movie_id, movie_to_insert)

                # find if the cinema is already associated with the movie
                movies_in_cinema = get_movies_in_cinema(cur, movie_id, cinema_id, location_id, date)
                if not movies_in_cinema:  # if the cinema is not associated with the movie, create it
                    insert_movies_in_cinema(conn, cur, movie_id, cinema_id, location_id, date, link_cinema_movie_page, language)

            cur.close()
            conn.close()
        except psycopg2.Error as e:
            print("Error:", e)


def get_movie_id_by_title(cur, title):
    """Retrieves a movie ID by title."""
    try:
        cur.execute("SELECT id FROM movies WHERE title = %s", (title,))
        row = cur.fetchone()
        if row:
            return row[0]
        return None
    except psycopg2.Error as e:
        print("Error:", e)
        return None


def insert_new_movie(conn, cur, movie_to_insert):
    """Inserts a new movie into the database and returns its ID."""
    try:
        cur.execute("""
        INSERT INTO movies (title, description, duration, original_lang, genre, classification, release_year, trailer_url, poster_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (movie_to_insert.title, movie_to_insert.description, movie_to_insert.duration, movie_to_insert.original_lang, 
          movie_to_insert.genre, movie_to_insert.classification, movie_to_insert.release_year, movie_to_insert.trailer_url, 
          movie_to_insert.poster_url))
        
        row = cur.fetchone()
        
        # Commit the transaction
        conn.commit()
        
        print("Insert successful")
        if row:
            return row[0]
        return None
    except psycopg2.Error as e:
        print("Error:", e)
        return None

def update_movie(conn, cur, movie_id, movie_to_insert):
    """Updates an existing movie in the database."""
    try:
         # We update movie values in case the new movie has them
        cur.execute("""
        UPDATE movies SET 
        title = %s, 
        description = %s, 
        duration = %s, 
        original_lang = %s, 
        genre = %s, 
        classification = %s, 
        release_year = %s, 
        trailer_url = %s, 
        poster_url = %s
        WHERE id = %s
    """, (movie_to_insert.title, movie_to_insert.description, movie_to_insert.duration, movie_to_insert.original_lang, 
          movie_to_insert.genre, movie_to_insert.classification, movie_to_insert.release_year, movie_to_insert.trailer_url, 
          movie_to_insert.poster_url, movie_id))
        
        # Commit the transaction
        conn.commit()
        
        print("Update successful")
    except psycopg2.Error as e:
        print("Error:", e)
   

def insert_movies_in_cinema(conn, cur, movie_id, cinema_id, location_id, date, link_cinema_movie_page, language):
    """Inserts a movie into the movies_in_cinema table."""
    try:
        # Check if the location_id exists in the cinema_locations table
        cur.execute("SELECT 1 FROM cinema_locations WHERE id = %s", (str(location_id),))
        location_exists = cur.fetchone()

        if location_exists:
            try:
                cur.execute("""
                    INSERT INTO movies_in_cinema (movie_id, cinema_id, location_id, date_title, cinema_movie_url, language)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (movie_id, cinema_id, location_id, date, link_cinema_movie_page, language))
                
                conn.commit()
                
                print("Insert successful")
            except psycopg2.Error as e:
                print("Error:", e)
        else:
            print("Error: Location with id {} does not exist.".format(location_id))
    except psycopg2.Error as e:
        print("Error:", e)


def get_movies_in_cinema(cur, movie_id, cinema_id, location_id, date):
    """Retrieve a movie from the movies_in_cinema table based on movie ID, cinema ID, location ID, and date."""
    try:
        cur.execute("""
            SELECT * FROM movies_in_cinema 
            WHERE movie_id = %s AND cinema_id = %s AND location_id = %s AND date_title = %s
        """, (movie_id, cinema_id, location_id, date))
        row = cur.fetchone()
        if row:
            return row
        return None
    except psycopg2.Error as e:
        print("Error:", e)
            
def clean_tables():
    """Delete all records from the movies, movies_in_cinema, and cinema_locations tables."""

    conn = get_db_connection()
    cur = conn.cursor()

    delete_movie_query = "DELETE FROM movies"
    delete_movies_in_cinema_query = "DELETE FROM movies_in_cinema"
    delete_cinema_location_query = "DELETE FROM cinema_locations"

    try:
        cur.execute(delete_movie_query)
        cur.execute(delete_movies_in_cinema_query)
        cur.execute(delete_cinema_location_query)
    except psycopg2.Error as e:
        print("Error:", e)
            
    conn.commit()

    cur.close()
    conn.close()
