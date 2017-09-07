from flask import Flask, render_template, url_for, request, redirect,\
    flash, jsonify

# Anti Forgery State Token imports
from flask import session as login_session
import random
import string
import os

# GConnect imports
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json

from flask import make_response
import requests

# Database imports
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User

app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = 'Item Catalog Application'


# Create an instance of the Flask class with name of running application
engine = create_engine('sqlite:///catalog_with_user.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/catalog')
def catalogCategories():
    """ Queries and renders list of categories """
    catalog = session.query(Category).all()
    items = session.query(Item).all()
    category = {'name': 'All'}
    return render_template('category_items.html',
                           categories=catalog,
                           items=items,
                           category=category)


@app.route('/category/<int:category_id>/', methods=['GET'])
def categoryItems(category_id):
    """ Queries and renders list of items in a particular category """
    if request.method == 'GET':
        categories = session.query(Category).all()
        items = session.query(Item).filter_by(category_id=category_id)
        category = session.query(Category).filter_by(id=category_id).one()
        return render_template('category_items.html',
                               items=items,
                               categories=categories,
                               category=category)


@app.route('/category/<int:category_id>/item/json', methods=['GET'])
def getcategoryJSON(category_id):
    """ Returns JSON object of a category and items within category """
    category = session.query(Item).filter_by(category_id=category_id)
    return jsonify(Items=[i.serialize for i in category])


@app.route('/category/<int:category_id>/item/<int:item_id>/json',
           methods=['GET'])
def getitemJSON(category_id, item_id):
    """ Returns JSON of a single item in a category """
    item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(Item=item.serialize)


@app.route('/category/<int:category_id>/edit/<int:item_id>/',
           methods=['GET', 'POST'])
def editItem(category_id, item_id):
    """ Allows user to edit an item in the database """
    if 'username' not in login_session:
        return redirect('/login')
    item_query = session.query(Item).filter_by(id=item_id).one()
    prev_name = item_query.name
    if login_session['user_id'] != item_query.user_id:
        return "<script>function myFunction() {" \
        "alert('You are not authorized to edit this item in the catalog. "\
        "You are allowed to edit items you have created.');}" \
        "</script><body onload='myFunction()''>"
    if request.method == 'GET':
        return render_template('editItem.html',
                               item=item_query,
                               category_id=category_id,
                               item_id=item_id)
    if request.method == 'POST':
        if request.form['name']:
            item_query.name = request.form['name']
        if request.form['description']:
            item_query.description = request.form['description']
        session.commit()
        return redirect(url_for('categoryItems', category_id=category_id))


@app.route('/catalog/add/', methods=['GET', 'POST'])
def addItem():
    """ Adds new item to database """
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newItem = Item(name=request.form['name'],
                       description=request.form['description'],
                       category_id=int(request.form['category_id']),
                       user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        return redirect(url_for('catalogCategories'))
    if request.method == 'GET':
        categories = session.query(Category)
        return render_template('addItem.html', categories=categories)


@app.route('/catalog/delete/<int:item_id>', methods=['GET', 'POST'])
def deleteItem(item_id):
    """ Removes item from database """
    if 'username' not in login_session:
        return redirect('/login')
    item_query = session.query(Item).filter_by(id=item_id).one()
    if login_session['user_id'] != item_query.user_id:
        return "<script>function myFunction() {"\
        "alert('You are not authorized to delete this item in the catalog. "\
        "You are allowed to delete items you have created.');}"\
        "</script><body onload='myFunction()''>"
    if request.method == 'GET':
        item_to_delete = session.query(Item).filter_by(id=item_id).one()
        return render_template('deleteItem.html', item=item_to_delete)
    if request.method == 'POST':
        item_to_delete = session.query(Item).filter_by(id=item_id).one()
        session.delete(item_to_delete)
        return redirect(url_for('catalogCategories'))


@app.route('/login')
def showLogin():
    """ Generates a random state session token and sends to user when\
     login is requested"""
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """ Process taken after user authenticates using Google Sign In and\
    validates access token and state token"""
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
            json.dumps('Token\'s user ID doesn\'t match given user ID.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps('Token\'s client ID does not match app\'s.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user \
                                 is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    # Store profile info
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])
    if not(user_id):
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px;\
                height: 300px;border-radius:150px;\
                -webkit-border-radius: 150px;\
                -moz-border-radius: 150px;"> '
    flash('you are now logged in as %s' % login_session['username'])
    return output


@app.route('/catalog/json')
def get_JSON():
    """ Return JSON for entire list of items in database """
    categories = session.query(Category).all()
    return jsonify(Categories=[i.serialize for i in categories])


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Current user\
                                 not connected.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
          % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
                                 'Failed to revoke token for given user.',
                                 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# User Helper Functions
def createUser(login_session):
    """ Creates a new user after user authenticates via Google Sign In"""
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# If not used as an imported module, run following code
if __name__ == '__main__':
    # Server reload on code changes
    app.secret_key = 'super_secret_key'
    app.debug = True
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
