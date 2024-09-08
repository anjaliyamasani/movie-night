from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import ast
import nltk
from sklearn.feature_extraction.text import CountVectorizer
from nltk.stem.porter import PorterStemmer
from sklearn.metrics.pairwise import cosine_similarity
from movie_poster import fetch_movie_poster

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"]) # This will allow your React app to communicate with Flask
# ----------------------- clean data ------------------------------------------------------------------
# Load your movie DataFrame
credits_df = pd.read_csv('anjaliCredits.csv')
movies_df = pd.read_csv('anjaliMovies.csv')

movies_df = movies_df.merge(credits_df, on='title')

# also see popularity and release date
movies_df = movies_df[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]

movies_df.dropna(inplace=True)

def convert(obj):
    L=[]
    for i in ast.literal_eval(obj):
        L.append(i['name'])
    return L

def convert3(obj):
    L=[]
    counter = 0
    for i in ast.literal_eval(obj):
        if counter < 3:
            L.append(i['name'])
            counter += 1
        else:
            break
    return L

movies_df['genres'] = movies_df['genres'].apply(convert)
movies_df['keywords'] = movies_df['keywords'].apply(convert)

movies_df['cast'] = movies_df['cast'].apply(convert3)

def fetch_director(obj):
    L=[]
    for i in ast.literal_eval(obj):
        if i['job'] == 'Director':
            L.append(i['name'])
    return L

movies_df['crew'] = movies_df['crew'].apply(fetch_director)

# separate overview with commas
movies_df['overview'] = movies_df['overview'].apply(lambda x:x.split())

movies_df['genres']=movies_df['genres'].apply(lambda x:[i.replace(" ","") for i in x])
movies_df['keywords']=movies_df['keywords'].apply(lambda x:[i.replace(" ","") for i in x])
movies_df['cast']=movies_df['cast'].apply(lambda x:[i.replace(" ","") for i in x])
movies_df['crew']=movies_df['crew'].apply(lambda x:[i.replace(" ","") for i in x])

movies_df['tags']=movies_df['overview']+movies_df['genres']+movies_df['keywords']+movies_df['cast']+movies_df['crew']

# create new data frame with only id, title, tags 
new_df = movies_df[['movie_id','title','tags']]
new_df['tags'] = new_df['tags'].apply(lambda x:' '.join(x))
new_df['tags']=new_df['tags'].apply(lambda X:X.lower())

# Extract movie titles for searching
movie_titles = new_df['title'].tolist()

@app.route('/api/search-movies', methods=['GET'])
def search_movies():
    query = request.args.get('query', '').lower()
    if query:
        # Filter movies that start with the query
        # CUSTOMIZE to filter for any part of the movie title 
        filtered_movies = [title for title in movie_titles if title.lower().startswith(query)]
        return jsonify(filtered_movies)
    return jsonify([])

# stop_words ignores words like a, an, the, is, and, etc

cv = CountVectorizer(max_features= 5000, stop_words='english')
cv.fit_transform(new_df['tags']).toarray().shape
vectors = cv.fit_transform(new_df['tags']).toarray()

ps = PorterStemmer()

def stem(text):
    y=[]
    for i in text.split():
        y.append(ps.stem(i))
    return " ".join(y)

new_df['tags'] = new_df['tags'].apply(stem)

similarity = cosine_similarity(vectors)

def recommend(movie):
    recs=[]
    movie_index=new_df[new_df['title']==movie].index[0]
    distances=similarity[movie_index]
    movies_list=sorted(list(enumerate(distances)), reverse=True, key=lambda x:x[1])[1:13]

    for i in movies_list:
        recs.append(new_df.iloc[i[0]].title)
    return recs

#try it out
recommend('Avatar')

# Function to get movie recommendations
# def get_movie_recommendations(title):
#     recommended_movies = new_df[new_df['title'].str.contains(title, case=False)]
#     return recommended_movies[['movie_id', 'title', 'tags']].to_dict(orient='records')



# Define an API endpoint
@app.route('/api/recommendations', methods=['GET'])
def recommendations():
    title = request.args.get('title')
    if title:
        try:
            results = recommend(title)
            recommendations_with_posters = [
                {
                    "title": movie_title,
                    "poster_url": fetch_movie_poster(movie_title)
                } for movie_title in results
            ]
            return jsonify(recommendations_with_posters)
        except IndexError:
            return jsonify({"error": "Movie not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "No title provided"}), 400

if __name__ == "__main__":
    app.run(debug=True)
