from flask import Flask, render_template, url_for, request, redirect,\
    flash, jsonify

app = Flask(__name__)

# Anti Forgery State Token imports
from flask import session as login_session
import random, string


# GConnect
from oauth2client.client import flow_from_clientsecrets
# Catches errors
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog Application"




# Database imports
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User

# Create an instance of the Flask class with name of running application
engine = create_engine('sqlite:///catalog_with_user.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Following function called HELLO world will be executed if any calls from the
# server have the route of / or /hello
@app.route('/')
def catalogCategories():
    catalog = session.query(Category)
    items = session.query(Item)
    return render_template('catalog.html', catalog=catalog)

@app.route('/category/<int:category_id>/', methods=['GET', 'POST'])
def categoryItems(category_id):
    if request.method == 'GET':
        categories = session.query(Category).all()
        items = session.query(Item).filter_by(category_id=category_id)
        if items.count():
            return render_template('category_items.html',
                                   items=items,
                                   categories=categories)
        else:
            return render_template('catalog.html', categories=categories)


@app.route('/category/<int:category_id>/edit/<int:item_id>/',
           methods=['GET', 'POST'])
def editItem(category_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    item_query = session.query(Item).filter_by(id=item_id).one()
    prev_name = item_query.name
    print item_query.user.name
    if login_session['user_id'] != item_query.user_id:
        return "<script>function myFunction() {alert('You are not authorized\
        to edit this item in the catalog. You are allowed to edit items\
        you have created');}</script><body onload='myFunction()''>"
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
    if 'username' not in login_session:
        return redirect('/login')
    item_query = session.query(Item).filter_by(id=item_id).one()
    if login_session['user_id'] != item_query.user_id:
        return "<script>function myFunction() {alert('You are not authorized\
        to edit this item in the catalog. You are allowed to edit items\
        you have created');}</script><body onload='myFunction()''>"
    if request.method == 'GET':
        item_to_delete = session.query(Item).filter_by(id=item_id).one()
        return render_template('deleteItem.html', item=item_to_delete)
    if request.method == 'POST':
        item_to_delete = session.query(Item).filter_by(id=item_id).one()
        session.delete(item_to_delete)
        return redirect(url_for('catalogCategories'))


# Anti Forgery State Token for CSRF
# Create a state variable that is passed to the client

@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

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
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
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
    print login_session['picture']
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
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
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
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# User Helper Functions
def createUser(login_session):
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



# If not used as an imported module run following code
if __name__ == '__main__':
    # Server reload on code changes
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
