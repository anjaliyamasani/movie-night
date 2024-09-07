import requests

API_KEY = '3540194d05dfb5ab4f6bd9bfd4570fc8'

def fetch_movie_poster(movie_title):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={movie_title}"
    response = requests.get(url)
    data = response.json()

    if data['results']:
        poster_path = data['results'][0]['poster_path']
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
    return None

