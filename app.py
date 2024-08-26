from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    release_year = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float, nullable=True)
    genres = db.relationship('Genre', secondary='movie_genres', back_populates='movies')
    actors = db.relationship('Actor', secondary='movie_actors', back_populates='movies')
    directors = db.relationship('Director', secondary='movie_directors', back_populates='movies')
    technicians = db.relationship('Technician', secondary='movie_technicians', back_populates='movies')

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    movies = db.relationship('Movie', secondary='movie_genres', back_populates='genres')

class Actor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    movies = db.relationship('Movie', secondary='movie_actors', back_populates='actors')

class Director(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    movies = db.relationship('Movie', secondary='movie_directors', back_populates='directors')

class Technician(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    movies = db.relationship('Movie', secondary='movie_technicians', back_populates='technicians')

class MovieGenre(db.Model):
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'), primary_key=True)

class MovieActor(db.Model):
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey('actor.id'), primary_key=True)

class MovieDirector(db.Model):
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), primary_key=True)
    director_id = db.Column(db.Integer, db.ForeignKey('director.id'), primary_key=True)

class MovieTechnician(db.Model):
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), primary_key=True)
    technician_id = db.Column(db.Integer, db.ForeignKey('technician.id'), primary_key=True)

# Create tables
with app.app_context():
    db.create_all()

# APIs

# Get All Movies
@app.route('/movies', methods=['GET'])
def get_movies():
    filters = []
    if 'actor' in request.args:
        actor_id = request.args.get('actor')
        filters.append(MovieActor.actor_id == actor_id)
    if 'director' in request.args:
        director_id = request.args.get('director')
        filters.append(MovieDirector.director_id == director_id)
    if 'technician' in request.args:
        technician_id = request.args.get('technician')
        filters.append(MovieTechnician.technician_id == technician_id)
        
    query = db.session.query(Movie).join(MovieActor, Movie.id == MovieActor.movie_id).join(MovieDirector, Movie.id == MovieDirector.movie_id).join(MovieTechnician, Movie.id == MovieTechnician.movie_id)
    
    if filters:
        query = query.filter(*filters)

    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    movies = query.paginate(page, per_page, False)
    result = [{'id': movie.id, 'name': movie.name, 'release_year': movie.release_year, 'rating': movie.rating} for movie in movies.items]
    return jsonify(result)

# Get a Specific Movie
@app.route('/movies/<int:movie_id>', methods=['GET'])
def get_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    return jsonify({'id': movie.id, 'name': movie.name, 'release_year': movie.release_year, 'rating': movie.rating})

# Add or Update a Movie
@app.route('/movies', methods=['POST'])
def add_or_update_movie():
    data = request.json
    movie_id = data.get('id')
    if movie_id:
        movie = Movie.query.get(movie_id)
        if not movie:
            return jsonify({'error': 'Movie not found'}), 404
        movie.name = data.get('name', movie.name)
        movie.release_year = data.get('release_year', movie.release_year)
        movie.rating = data.get('rating', movie.rating)
    else:
        movie = Movie(
            name=data['name'],
            release_year=data['release_year'],
            rating=data.get('rating')
        )
        db.session.add(movie)
    db.session.commit()
    return jsonify({'id': movie.id, 'name': movie.name, 'release_year': movie.release_year, 'rating': movie.rating})

# Delete a Movie
@app.route('/movies/<int:movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return jsonify({'message': 'Movie deleted successfully'})

# Delete an Actor
@app.route('/actors/<int:actor_id>', methods=['POST'])
def delete_actor(actor_id):
    actor = Actor.query.get_or_404(actor_id)
    if actor.movies:
        return jsonify({'message': 'Actor cannot be deleted because they are associated with movies.'}), 400
    db.session.delete(actor)
    db.session.commit()
    return jsonify({'message': 'Actor deleted successfully'})

if __name__ == '__main__':
    app.run(debug=True)
