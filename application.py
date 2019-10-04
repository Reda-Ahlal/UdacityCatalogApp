from flask import Flask, render_template, request, redirect, url_for


from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Movie, User


from flask import session as login_session
import random
import string


from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response, jsonify, flash
import requests


# init app
app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog App"


# Connect to Database and create database session
engine = create_engine('sqlite:///moviescatalog.db')
Base.metadata.bind = engine


# Home Page Application
@app.route('/')
@app.route('/Catalog/')
def showCatalog():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    categories = session.query(Category).all()
    latest_movies_added = session.query(
            Movie.name.label("Movie_name"),
            Category.name.label("Category_name"),
            Movie.user_id.label("user_id")). \
        join(Category). \
        filter(Movie.category_id == Category.id). \
        order_by(Movie.created_date.desc()).all()
    Users = session.query(User).all()
    creators = []
    for l in latest_movies_added:
        for u in Users:
            if l.user_id == u.id:
                creators.append(u.name)
    return render_template(
                            'catalog.html',
                            categories=categories,
                            latest_movies_added=latest_movies_added,
                            creators=creators)


# Show Movies By Category
@app.route('/Catalog/<string:category_name>')
def showMoviesByCategory(category_name):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    categories = session.query(Category).all()
    movies = session.query(Movie.name). \
        join(Category).filter(
                        Movie.category_id == Category.id,
                        Category.name == category_name).all()
    nbrMovies = len(movies)
    return render_template(
                            'moviesByCategory.html',
                            categories=categories,
                            category_name=category_name,
                            movies=movies,
                            nbrMovies=nbrMovies)


# Show Movie Description
@app.route('/Catalog/<string:category_name>/<string:movie_name>')
def showMoviesDescription(category_name, movie_name):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    categories = session.query(Category).all()
    movie = session.query(Movie).filter_by(name=movie_name).one()
    user = session.query(User).filter_by(id=movie.user_id).one()
    return render_template(
                            'movieDescription.html',
                            movie=movie,
                            categories=categories,
                            category_name=category_name,
                            user=user)


# Show User's Movies
@app.route('/<string:user_name>')
def showMoviesByUser(user_name):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    categories = session.query(Category).all()
    user = session.query(User).filter_by(name=user_name).one()
    movies = session.query(
                            Movie.name.label("movie_name"),
                            Category.name.label("category_name")). \
        join(Category). \
        filter(
                   Movie.category_id == Category.id,
                   Movie.user_id == user.id).all()
    nbrMovies = len(movies)
    return render_template(
                            'moviesByUser.html',
                            categories=categories,
                            movies=movies,
                            nbrMovies=nbrMovies,
                            user_name=user_name)


# Edit Movie
@app.route(
            '/Catalog/<string:category_name>/<string:movie_name>/edit',
            methods=['GET', 'POST'])
def editMovie(category_name, movie_name):
    if 'username' not in login_session:
        return redirect('/login')
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    categories = session.query(Category).all()
    editedMovie = session.query(Movie).filter_by(name=movie_name).one()
    if editedMovie.user_id != login_session['user_id']:
        user = getUserInfo(login_session['user_id'])
        user_id = login_session['user_id']
        movies = session.query(
                                Movie.name.label("movie_name"),
                                Category.name.label("category_name")). \
            join(Category). \
            filter(
                        Movie.category_id == Category.id,
                        Movie.user_id == user_id). \
            order_by(Movie.created_date.desc()).all()
        nbrMovies = len(movies)
        flash('''You are not authorized to edit this Movie,
                 try with your movies list below.''')
        return render_template(
                                'moviesByUser.html',
                                categories=categories,
                                movies=movies,
                                nbrMovies=nbrMovies,
                                user_name=user.name)
    if request.method == 'POST':
        if request.form['name']:
            editedMovie.name = request.form['name']
        if request.form['year']:
            editedMovie.year = request.form['year']
        if request.form['director']:
            editedMovie.director = request.form['director']
        if request.form['description']:
            editedMovie.description = request.form['description']
        if request.form['category']:
            category = session.query(Category). \
                filter_by(name=request.form['category']).one()
            editedMovie.category_id = category.id
        session.add(editedMovie)
        session.commit()
        flash('"%s" Movie Successfully Edited ' % editedMovie.name)
        return redirect(url_for(
                                'showMoviesByCategory',
                                categories=categories,
                                category_name=category.name))
    else:
        return render_template(
                                'editMovie.html',
                                movie=editedMovie,
                                categories=categories,
                                category_name=category_name)


# Delete Movie
@app.route(
            '/Catalog/<string:category_name>/<string:movie_name>/delete',
            methods=['GET', 'POST'])
def deleteMovie(category_name, movie_name):
    if 'username' not in login_session:
        return redirect('/login')
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    categories = session.query(Category).all()
    movieToDelete = session.query(Movie).filter_by(name=movie_name).one()
    if movieToDelete.user_id != login_session['user_id']:
        user = getUserInfo(login_session['user_id'])
        user_id = login_session['user_id']
        movies = session.query(
                                Movie.name.label("movie_name"),
                                Category.name.label("category_name")).\
            join(Category). \
            filter(
                       Movie.category_id == Category.id,
                       Movie.user_id == user_id). \
            order_by(Movie.created_date.desc()).all()
        nbrMovies = len(movies)
        flash('''You are not authorized to delete this Movie,
                 try with your movies list below.''')
        return render_template(
                                'moviesByUser.html',
                                categories=categories,
                                movies=movies,
                                nbrMovies=nbrMovies,
                                user_name=user.name)
    if request.method == 'POST':
        session.delete(movieToDelete)
        session.commit()
        flash('"%s" Movie Successfully Deleted' % movieToDelete.name)
        return redirect(url_for(
                                'showMoviesByCategory',
                                category_name=category_name))
    else:
        return render_template(
                                'deleteMovie.html',
                                categories=categories,
                                movie=movieToDelete,
                                category_name=category_name)


# Add a New Movie
@app.route('/Catalog/new/', methods=['GET', 'POST'])
def addMovie():
    if 'username' not in login_session:
        return redirect('/login')
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    categories = session.query(Category).all()
    if request.method == 'POST':
        category = session.query(Category). \
            filter_by(name=request.form['category']).one()
        user_id = login_session['user_id']
        newMovie = Movie(name=request.form['name'],
                         year=request.form['year'],
                         director=request.form['director'],
                         description=request.form['description'],
                         category_id=category.id,
                         user_id=user_id)
        session.add(newMovie)
        session.commit()
        flash('"%s" Movie Successfully Created' % (newMovie.name))
        return redirect(url_for('showCatalog'))
    else:
        return render_template('addMovie.html', categories=categories)


# Show Categories JSON endpoint
@app.route('/Categories/json')
def showCategoriesJSON():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    Categories = session.query(Category).all()
    return jsonify(Categories=[c.serialize for c in Categories])


# Show Movies JSON endpoint
@app.route('/Movies/json')
def showMoviesJSON():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    Movies = session.query(Movie).all()
    return jsonify(Movies=[c.serialize for c in Movies])


# Show Catalog JSON endpoint
@app.route('/Catalog/json')
def showCatalogJSON():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    Categories = session.query(Category).all()
    Catalog = []
    for c in Categories:
        Catalog.append(c.serialize)
        Movies = session.query(Movie).filter_by(category_id=c.id).all()
        Catalog[-1]['Movies'] = [m.serialize for m in Movies]
    return jsonify(Categories=Catalog)


# Show Arbitrary Movie in The Catalog JSON endpoint
@app.route('/Catalog/<string:movie_name>/json')
def showMovieInCatalogJSON(movie_name):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    movie = session.query(Movie).filter_by(name=movie_name).one()
    return jsonify(Movie=movie.serialize)


# Login
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# GCONNECT - Define gconnect method for Google sign in
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
                                'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't create a new user
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    creator_name = login_session['username']
    creator_pic = login_session['picture']

    output = ''
    output += '<h2>Welcome, '
    output += login_session['username']
    output += '!</h2>'
    output += '<img src="'
    output += login_session['picture']
    output += '"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['gplus_id']
        del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCatalog'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCatalog'))


# User Helper Functions
def createUser(login_session):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    newUser = User(
                    name=login_session['username'],
                    email=login_session['email'],
                    picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Run The Server
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
