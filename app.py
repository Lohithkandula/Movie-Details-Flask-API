import os
import requests
from flask import Flask
from flask_restful import Api, Resource
from flask_httpauth import HTTPTokenAuth

app = Flask(__name__)
api = Api(app)
auth = HTTPTokenAuth(scheme='Bearer')

# Retrieve the API key from environment variable
API_KEY = os.environ.get('MOVIE_API_KEY')
if not API_KEY:
    raise ValueError('Movie API key is missing. Set the MOVIE_API_KEY environment variable.')

# Verify the API key
@auth.verify_token
def verify_token(token):
    return token == API_KEY

@auth.error_handler
def unauthorized():
    return {'message': 'Unauthorized'}, 401

# Endpoint for movie details
class MovieDetails(Resource):
    @auth.login_required
    def get(self, movie_name):
        url = f'https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={movie_name}'
        response = requests.get(url)
        data = response.json()
        if 'results' in data and len(data['results']) > 0:
            movie = data['results'][0]
            movie_details = {
                'title': movie['title'],
                'release_year': movie['release_date'].split('-')[0],
                'plot': movie['overview'],
                'cast': self.get_movie_cast(movie['id']),
                'rating': movie['vote_average']
            }
            return movie_details
        else:
            return {'message': 'Movie not found'}, 404

    def get_movie_cast(self, movie_id):
        url = f'https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={API_KEY}'
        response = requests.get(url)
        data = response.json()
        cast = []
        if 'cast' in data:
            for actor in data['cast'][:5]:
                cast.append(actor['name'])
        return cast

# Endpoint for movie list
class MovieList(Resource):
    @auth.login_required
    def get(self):
        url = f'https://api.themoviedb.org/3/discover/movie?api_key={API_KEY}&sort_by=popularity.desc'
        response = requests.get(url)
        data = response.json()
        movie_list = []
        if 'results' in data:
            for movie in data['results'][:10]:
                movie_list.append(movie['title'])
        return {'movies': movie_list}

# Add routes to the Flask application
api.add_resource(MovieDetails, '/movies/<string:movie_name>')
api.add_resource(MovieList, '/movies')

if __name__ == '__main__':
    app.run(debug=True)
