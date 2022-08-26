from dotenv import load_dotenv
from os import environ
from flask import Flask, flash, render_template, request, url_for, redirect, session
from models.models import Db, User, Image, Classification
from forms.forms import SignupForm, LoginForm, ImageUploadForm
from os import environ
from passlib.hash import sha256_crypt
import requests
from flask_wtf.csrf import CSRFProtect
from datetime import date, datetime
import tensorflow as tf
import tensorflow_hub as hub
from PIL import Image
from models import models
import os
import pandas as pd
import numpy as np
import json
import plotly
import plotly.express as px
import gunicorn
import psycopg2

# Load environment
load_dotenv('.env')

# Initialize app
app = Flask(__name__)
csrf = CSRFProtect(app) # have to wrap it or it fails on create https://stackoverflow.com/questions/21501058/form-validation-fails-due-missing-csrf
app.secret_key = environ.get('SECRET_KEY')

# Initialize DB
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL').replace('postgres://', 'postgresql://') # this is to solve a bug in heroku
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Db.init_app(app)

# Directory variables
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
app.config['STATIC_FOLDER'] = '/static'
app.config['IMAGE_FOLDER'] = '/static/images'
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
IMAGES_ROOT = os.path.join(STATIC_ROOT, 'images')


# set some constants
MAX_STRING_LENGTH   = 64
MIN_PASSWORD_LENGTH = 8 # set something reasonable
MAX_PASSWORD_LENGTH = 128 # see models/model.py
ITEMS_PER_PAGE = 15 # Set the items per page limit

# Load ML model
model_path = os.path.join( app.root_path, 'models', 'model.hdf5')
model = tf.keras.models.load_model(model_path, custom_objects={'KerasLayer':hub.KerasLayer})
#model = tf.keras.models.load_model('./models/model.hdf5', custom_objects={'KerasLayer':hub.KerasLayer})

# Initialize classification classes
classes = np.array(['complex', 'frog_eye_leaf_spot', 'healthy', 'powdery_mildew', 'rust', 'scab'])

# From lab5
def check_string( str = None, label = "", max_length = MAX_STRING_LENGTH ):
    # can't have a null value!
    if str == None:
        raise ValueError( f'Variable {label} cannot be null!' )
    
    # strip the string of leading & trailing whitespace
    str = str.strip()
        
    if str == "":
        raise ValueError( f'Variable {label} is empty!' )
    elif len( str ) > max_length:
        raise ValueError( f'Variable {label} is too long! {len(str)} > {max_length}' )
    
    return str
    
def check_int( num = None, label = "", min = float('-inf'), max = float('inf') ):
    try:
        num = int( num )
    except:
        raise ValueError( f'Variable {label} malformed! ({num})' )

        
    if num < min or num > max:
        raise ValueError( f'Variable {label} is out of range! ({num} <> [{min},{max}])' )
        
    return num
        
def check_float( num = None, label = "", min = float('-inf'), max = float('inf') ):
    try:
        num = float( num )
    except:
        raise ValueError( f'Variable {label} malformed! ({num})' )
    
    if num < min or num > max:
        raise ValueError( f'Variable {label} is out of range! ({num} <> [{min},{max}])' )
        
    return num
    
# NEW Get Error from exception
def get_error(e):
    return e.message if hasattr(e, 'message') else str(e)
    
# NEW Check Password
# This is only to sanitize passwords for NEW users. Why don't we want to do these checks
# when someone is authenticating? (Hint: security)
def check_password( password = None, label = "password", min_length = MIN_PASSWORD_LENGTH , max_length = MAX_PASSWORD_LENGTH ):
    # can't have a null value!
    if password == None:
        raise ValueError( f'Variable {label} cannot be null!' )
    
    # we don't want to strip any characters from the password!
    
    # string can't be empty    
    if password == "":
        raise ValueError( f'Variable {label} is empty!' )
    
    # Need a minimum number of chars
    if len( password ) < min_length:
        raise ValueError( f'Variable {label} is too short! {len(password)} < {min_length}' )
    
    # Need a maximum number of chars
    if len( password ) > max_length:
        raise ValueError( f'Variable {label} is too long! {len(password)} > {max_length}' )
    
    return password
    
# This is to ensure the passwords are both valid and the same
def verify_password( password = None, verify = None, min_length = MIN_PASSWORD_LENGTH, max_length = MAX_PASSWORD_LENGTH ):
    password    = check_password( password, 'password', min_length, max_length )
    verify      = check_password( verify, 'verify', min_length, max_length )
    
    if password != verify:
        raise ValueError( 'Passwords do not match!' )
        
    return password, verify # returns both password & verification

    
# Get the currently logged in user
def logged_in_user():
    # Three checks:
    # 1. if the username key exists in a session
    # 2. if the username isn't empty
    # 3. if the username is actually valid
    if 'username' in session and session['username'] != "":
        # Will return None if no such user exists
        return User.query.filter_by( username = session['username'] ).first()
    else:
        return None
        
# Unimplemented feature
def unimplemented_feature():
    try:
        # lots to do here!
        raise RuntimeError( "Unimplemented feature!" )
    
    # Any error
    except Exception as e:
        # show the error
        flash( get_error( e ), 'danger' )
        
        # redirect back to login page        
        return redirect( url_for( 'index' ) ) 

# User CRUD
# Create a new user /user/create
@app.route( '/user/create', methods=['POST'])
def user_create():
    try:
        # Init credentials from form request
        username = check_string( request.form['username'], 'username', MAX_STRING_LENGTH )
        password, verify = verify_password( request.form['password'], request.form['verify'], MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH )
        
        # Does the user already exist?
        user = User.query.filter_by( username = username ).first()
        if user:
            raise LookupError( f'User with username "{username}" already exists! Please choose another username.' )   
            
        # User is unique, so let's create a new one
        user = User( username=username, password=sha256_crypt.hash( password ) )
        Db.session.add( user )
        Db.session.commit()
        
        # Message Flashing
        # https://flask.palletsprojects.com/en/2.0.x/patterns/flashing/#flashing-with-categories
        flash( 'Congratulations, you are now a registered user!', 'success' )
        
        # Redirect to login page
        return redirect( url_for( 'login' ) )    
    except Exception as e:
        # show the error
        flash( get_error( e ), 'danger' )
        
        # redirect back to signup page
        return redirect( url_for( 'signup' ) )

        
# HW: Complete CRUD methods for User class
# NOTE: Each of the following routes should redirect the user to the login page if the user is not logged in!

# HW: Add /user/retrieve/<username>
@app.route( '/user/retrieve/<username>' )
def user_retrieve( username ):
    try:
        # user must be logged in to view user profiles!
        user = logged_in_user()
        if user == None:
            raise KeyError( 'You are not logged in!' ) # session key not found!
           
        # sanitize input
        username = check_string( username, 'username' )
        
        # The logged in user can only see their own profile!
        profile_user = User.query.filter_by( username = username ).first()
        if profile_user == None:
            raise KeyError( "User does not exist!" )
        # if username != user.username:
        #     raise PermissionError( 'Unauthorized action!' )
        
        return render_template( "profile.html", user=user, profile_user=profile_user, title=f'@{profile_user.username}' )
    
    # Not logged in, go to login page
    except KeyError as ke:
        # show the error
        flash( get_error( ke ), 'danger' )
        
        return redirect( url_for( 'login' ) )
    
    # Not authorized, go to index page, could be combined with below
    except PermissionError as pe:
        # show the error
        flash( get_error( pe ), 'danger' )
        
        # redirect to index
        # how would we go back to the page we were just at?
        # See: https://tedboy.github.io/flask/generated/generated/flask.Request.referrer.html
        return redirect( url_for( 'index' ) )

    # Any other error
    except Exception as e:
        # show the error
        flash( get_error( e ), 'danger' )
        
        # redirect back to signup page
        return redirect( url_for( 'index' ) )

# HW: Add /user/update
@app.route( '/user/update/<username>', methods=['POST'])
def user_update( username ):
    try:
        # user must be logged in to view user profiles!
        user = logged_in_user()
        if user == None:
            raise KeyError( 'You are not logged in!' )
            
        # sanitize input
        username = check_string( request.form['username'], 'username' )
        # if we had additional information for updating, it would be here!
        # variable1 = check_???( request.form['variable1'], 'variable1'
        # variable2 = check_???( request.form['variable2'], 'variable2'
        # variable3 = check_???( request.form['variable3'], 'variable3'
        
        # The logged in user can only update their own profile!
        if username != user.username:
            raise PermissionError( 'Unauthorized action!' )
            
        # Hrm..! There's not much to do here! Why don't we want to modify passwords here??? Where would we do it instead?
        # See below
        # if we did have extra variables to update:
        # user.variable1 = variable1
        # user.variable2 = variable2
        # user.variable3 = variable3
        # Db.session.commit()
        
        # Go back to user profile
        return redirect( url_for( f'user/retrieve/{username}' ) )
    
    # Not authorized, go to login page
    except KeyError as ke:
        # show the error
        flash( get_error( ke ), 'danger' )
        
        # redirect to login
        return redirect( url_for( 'login' ) )
    
    # Any other error
    except Exception as e:
        # show the error
        flash( get_error( e ), 'danger' )
        
        # redirect back to index page (or referrer)
        # if we use this a lot, what could we do?
        last_page = request.referrer if request.referrer else url_for( 'index' )
        return redirect( last_page )

# Update User password
# Q: How would we update the username??
@app.route( '/user/update_password/<username>', methods = [ 'POST' ] )
def user_update_pasword( username ):
    try:
        # user must be logged in to view user profiles!
        user = logged_in_user()
        if user == None:
            raise KeyError( 'You are not logged in!' )
        
        # sanitize username
        username = check_string( request.form['username'], 'username' )
        
        # we can only change our own passwords!
        if( username != user.username ):
            raise PermissionError( 'Unauthorized action!' )
        
        # sanitize & check that the passwords match
        password, verify = verify_password( request.form['password'], request.form['verify'], MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH )  
        
        # set the password
        user.password = sha256_crypt.hash( password )
        
        # commit to Db
        Db.session.commit()
        
        # flash a message to the user
        flash( 'Password successfully changed!', 'success' )
            
        # return the blab as a json
        return redirect( url_for( f'user/retrieve/{username}' ) )
    
    # Not authorized, go to login page
    except KeyError as ke:
        # show the error
        flash( get_error( ke ), 'danger' )
        
        # redirect to login
        return redirect( url_for( 'login' ) )
    
    # Any other error
    except Exception as e:
        # show the error
        flash( get_error( e ), 'danger' )
        
        # redirect back to index page (or referrer)
        # if we use this a lot, what could we do?
        last_page = request.referrer if request.referrer else url_for( 'index' )
        return redirect( last_page )
    
# HW: Add /user/delete
# NOTE: This method is DANGEROUS! How could we make it less so?
@app.route( '/user/delete/<username>' )
def user_delete( username ):
    try:
        # user must be logged in to view user profiles!
        user = logged_in_user()
        if user == None:
            raise KeyError( 'You are not logged in!' )
        
        # sanitize username
        username = check_string( request.form['username'], 'username' )
        
        # we're the only ones who can delete our own user!
        if( username != user.username ):
            raise PermissionError( 'Unauthorized action!' )
                
        # Delete the user
        Db.session.delete( user )
        
        # Commit the changes
        Db.session.commit()
        
        # Our user is dead, so we need to log out!
        return redirect( url_for( 'logout' ) )
            
    # Not authorized, go to login page
    except KeyError as ke:
        # show the error
        flash( get_error( ke ), 'danger' )
        
        # redirect to login
        return redirect( url_for( 'login' ) )
    
    # Any other error
    except Exception as e:
        # show the error
        flash( get_error( e ), 'danger' )
        
        # redirect back to index page (or referrer)
        # if we use this a lot, what could we do?
        last_page = request.referrer if request.referrer else url_for( 'index' )
        return redirect( last_page )   


# Default route
@app.route('/')
@app.route('/index')
def index():
    user = logged_in_user()

    # Fetch weather widget photo
    weather_img_name = 'testweather2.PNG'
    weather_img_path = os.path.join('static/assets/img', weather_img_name) # for rendering template

    # generate plot from image submission query
    if user != None: # if a user is currently logged in
        images_query = models.Image.query.filter_by(uid=user.uid) # return only records for the current user
    else: # if no user is currently logged in
        images_query = models.Image.query # return all records submitted to the app
    df = pd.read_sql_query(images_query.statement, images_query.session.bind, index_col='image_id')
    fig = px.bar(df, x='classification_name', color='classification_name', 
      barmode='group')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # render template
    return render_template('index.html', user=user, weather_img_path=weather_img_path, graphJSON=graphJSON)


# Log a user in, if already logged in, log the current user out first!
# GET returns the login form
# blab processes the login form input
@app.route('/login', methods=['GET', 'POST'])
def login():    
    try:
        if request.method == 'POST':
            # Init & sanitize credentials from form request
            username = check_string( request.form['username'], 'username' )
            password = check_password( request.form['password'], 'password' )
            
            # Get the user user by Db query
            user = User.query.filter_by( username=username ).first()
            if user == None:
                raise KeyError( 'Invalid username or password' )
            
            # Control login validity
            # we have some unhashed passwords in the database, so we may need to fix them
            if user.password == password:
                user.password = sha256_crypt.hash( password ) # password wasn't hashed so we need to do it now
                Db.session.commit() # save the password hash
                user = User.query.filter_by( username=username ).first() # get the user back again
            
            # check the password against the hashed version
            if not sha256_crypt.verify( password, user.password ):
                raise PermissionError( 'Invalid username or password' )
                
            
            # set the logged in user's username in the session   
            session[ 'username' ] = username
            
            # let the user know login was sucessful
            flash( f'{username} is now logged in!', 'success' )
            
            # go to the index page
            return redirect(url_for('index'))
                
        else: # GET
            # Get the logged in user
            user = logged_in_user()
            
            # Init form
            form = LoginForm()
            
            # Show the login form
            return render_template( 'login.html', title='Login', form=form, user=user )
    
    # Any error
    except Exception as e:
        # show the error
        flash( get_error( e ), 'danger' )
        
        # redirect back to login page        
        return redirect( url_for( 'login' ) ) 

#blab /logout
@app.route( '/logout' )
def logout():
    # Clear all session data
    session.clear()
    
    # Go back to index page
    #return redirect( url_for( 'index' ) )

    # Go back to login page
    return redirect( url_for( 'login' ) )

# Register as a new user /signup
@app.route('/user/form/signup')
def signup():
    # Init form
    form = SignupForm()

    return render_template( 'signup.html', title='Signup', form=form )

# Route for image upload form
@app.route('/upload_image', methods = ['GET'])
def upload():
    user = logged_in_user()
    form = ImageUploadForm()
    if form.validate_on_submit():
        #filename = images.save(form.image.data)

        assets_dir = os.path.join(
            os.path.dirname(app.instance_path), 'static/images'
        )

    return render_template('image_upload_form.html', user=user, form=form)

# Route for generating and returning diagnosis/classification/prediction
@app.route('/diagnose', methods=['POST'])
def get_output():
    # Read and prepare image
    file = request.files['Image']
    filename = file.filename
    filepath = os.path.join('static/images', filename) # for rendering template
    filepath2 = os.path.join(PROJECT_ROOT + '/' + app.config['IMAGE_FOLDER'], filename) # for heroku upload
    file.save(filepath2)
    img = Image.open(file)
    img = img.resize((160,160))
    img = np.asarray(img)
    img = img/255
    img = np.expand_dims(img, axis=0)
    
    # Generate prediction
    prediction = (model.predict(img) > 0.5).astype('int')
    prediction = pd.Series(prediction[0])
    prediction.index = classes
    prediction = prediction[prediction==1].index.values
    
    # Get classifications
    classifications = list(prediction)
    if len(list(prediction)) == 0:
        classifications = ["The classification failed. Please provide another clearer image."]
    else:
        classifications
    
    # get full info by classifications
    q = Classification.query.filter(Classification.classification_name.in_(classifications))
    q_all = q.all()

    # Write to image table if user session is active
    user = logged_in_user()
    if user != None: # If a user session is currently active
        for classification in classifications:
            uid = user.uid
            username = user.username
            classification_name = classification
            newimage = models.Image(uid=uid, username=username, image_name=filename, classification_name=classification_name)
            Db.session.add(newimage)
            Db.session.commit()

    return render_template(
        "diagnose.html", 
        user=user,
        image_path=filepath,
        classifications=classifications, 
        info=q_all
        )

# Read classification information table
@app.route('/classification_table', defaults={ 'offset' : 0, 'limit' : ITEMS_PER_PAGE }, methods=['GET'] )
@app.route('/classification_table/<offset>', defaults={ 'limit' : ITEMS_PER_PAGE }, methods=['GET'] )
@app.route('/classification_table/<offset>/<limit>', methods=['GET'] )
def class_list( offset, limit ):
    user = logged_in_user()
    # sanitize inputs!
    try:
        offset = int( offset )
    except ValueError:
        offset = 0
    
    try:
        limit = int( limit )
    except:
        limit = ITEMS_PER_PAGE
    
    # ensure offset & limit aren't negative
    offset = offset if offset > 0 else 1 
    limit = limit if limit > 0 else ITEMS_PER_PAGE
    
    # get the pagination limits
    total = Classification.query.count() # count the total number of records
    
    # what do we do if the offset >= than the total??
    if total <= offset:
       return redirect( f'/classification_table/{total - limit}/{limit}' )
    
    pages = { 'begin' : 0 };
    pages[ 'prev' ] = max( offset - limit, 0 ) # don't want a negative index!
    pages[ 'current' ] = min( max( 0, offset ), total ) # gotta be in range!
    pages[ 'next' ] = min( offset + limit, total - limit ) # don't want to go over
    pages[ 'end' ] = total - limit # just get the end.
    
    # get just the users we want to show
    classes = Classification.query.offset( offset ).limit( limit )
    
    return render_template( "classification_table.html", user=user, classes=classes, pages=pages, limit=limit )

# Read users
@app.route('/users', defaults={ 'offset' : 0, 'limit' : ITEMS_PER_PAGE }, methods=['GET'] )
@app.route('/users/<offset>', defaults={ 'limit' : ITEMS_PER_PAGE }, methods=['GET'] )
@app.route('/users/<offset>/<limit>', methods=['GET'] )
def user_list( offset, limit ):
    user = logged_in_user()
    # Example: sanitize the inputs
    try:
        offset = int( offset ) # could fail
    except ValueError:
        offset = 0
    
    try:
        limit = int( limit )
    except:
        limit = ITEMS_PER_PAGE
    
    # ensure offset & limit aren't negative
    offset = offset if offset > 0 else 1
    limit = limit if limit > 0 else ITEMS_PER_PAGE
    
    # get the pagination limits
    total = User.query.count() # count the total number of records
    
    # what do we do if the offset >= than the total??
    if total <= offset:
       return redirect( f'/users/{total - limit}/{limit}' )
    
    pages = { 'begin' : 0 };
    pages[ 'prev' ] = max( offset - limit, 0 ) # don't want a negative index!
    pages[ 'current' ] = min( max( 0, offset ), total ) # gotta be in range!
    pages[ 'next' ] = min( offset + limit, total - limit ) # don't want to go over
    pages[ 'end' ] = total - limit # just get the end.
    
    # get just the users we want to show
    users = User.query.offset( offset ).limit( limit )
    
    return render_template( "user_table.html", user=user, users=users, pages=pages, limit=limit )

# Read images
@app.route('/images', defaults={ 'offset' : 0, 'limit' : ITEMS_PER_PAGE }, methods=['GET'] )
@app.route('/images/<offset>', defaults={ 'limit' : ITEMS_PER_PAGE }, methods=['GET'] )
@app.route('/images/<offset>/<limit>', methods=['GET'] )
def image_list( offset, limit ):
    user = logged_in_user()
    # Example: sanitize the inputs
    try:
        offset = int( offset ) # could fail
    except ValueError:
        offset = 0
    
    try:
        limit = int( limit )
    except:
        limit = ITEMS_PER_PAGE
    
    # ensure offset & limit aren't negative
    offset = offset if offset > 0 else 1
    limit = limit if limit > 0 else ITEMS_PER_PAGE
    
    # get the pagination limits
    total = models.Image.query.count() # count the total number of records
    
    # what do we do if the offset >= than the total??
    if total <= offset:
       return redirect( f'/images/{total - limit}/{limit}' )
    
    pages = { 'begin' : 0 };
    pages[ 'prev' ] = max( offset - limit, 0 ) # don't want a negative index!
    pages[ 'current' ] = min( max( 0, offset ), total ) # gotta be in range!
    pages[ 'next' ] = min( offset + limit, total - limit ) # don't want to go over
    pages[ 'end' ] = total - limit # just get the end.
    
    # get just the users we want to show
    images = models.Image.query.filter_by(uid=user.uid).offset( offset ).limit( limit )
    
    return render_template( "image_table.html", user=user, images=images, pages=pages, limit=limit )


@app.route('/dash')
# dashboard
def dash():
    user = logged_in_user()
    images_query = models.Image.query.filter_by(uid=user.uid)
    images = models.Image.query.all()
    #df_from_records = pd.DataFrame.from_records(images, index='image_id', columns=[
    #    'image_id', 'uid', 'image_name', 'image_submitted_date', 'image_classification_id', 'classification_name', 'username'
    #    ])
    df_from_query = pd.read_sql_query(images_query.statement, images_query.session.bind, index_col='image_id')

    fig = px.bar(df_from_query, x='classification_name', color='classification_name', 
      barmode='group')
    
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('dash.html', graphJSON=graphJSON)


# Errors
#@login_manager.unauthorized_handler
#def unauthorized_handler():
#    return render_template('home/page-403.html'), 403


@app.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403


@app.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500