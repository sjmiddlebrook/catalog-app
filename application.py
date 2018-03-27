import random
import string
import json
from datetime import datetime

import requests
import httplib2

from flask import Flask, render_template, jsonify, request, redirect, url_for, \
    flash, make_response
from flask import session as login_session
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Country, CatalogItem

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Travel Catalog Application"

# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create a state token to prevent request forgery
# Store the state in the session for later validation
@app.route('/login')
def show_login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for i in range(32))
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
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}'.
           format(access_token))
    h = httplib2.Http()
    req = h.request(url, 'GET')[1]
    req_json = req.decode('utf8').replace("'", '"')
    result = json.loads(req_json)
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
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'),
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
    login_session['email'] = data['email']
    flash("you are now logged in as {}".format(login_session['username']))
    return "successful login"


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps('Current user not connected.'),
            401)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('show_categories'))
    print('In gdisconnect access token is {}'.format(access_token))
    print('User name is: ')
    print(login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % \
          login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("you are now logged out.")
        return redirect(url_for('show_categories'))
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/countries/<int:country_id>/JSON')
def country_json(country_id):
    country = session.query(Country).filter_by(id=country_id).one()
    return jsonify(Country=country.serialize)


@app.route('/countries/<int:country_id>/cities/JSON')
def country_cities_json(country_id):
    cities = session.query(CatalogItem).filter_by(
        country_id=country_id).all()
    return jsonify(Cities=[i.serialize for i in cities])


@app.route('/countries/JSON')
def countries_json():
    countries = session.query(Country).all()
    return jsonify(Countries=[i.serialize for i in countries])


# Show all categories
@app.route('/')
@app.route('/countries/')
def show_categories():
    countries = session.query(Country).all()
    # select cities with latest updated cities first
    city_catalog_items = session.query(CatalogItem).order_by(
        desc(CatalogItem.last_update)).all()
    # check user is logged in
    if 'username' in login_session.keys():
        user = login_session['username']
    else:
        user = None
    return render_template('countries.html', countries=countries,
                           items=city_catalog_items, user=user)


# Add a new country
@app.route('/countries/new/', methods=['GET', 'POST'])
def add_country():
    if request.method == 'POST':
        new_country = Country(name=request.form['name'])
        session.add(new_country)
        session.commit()
        return redirect(url_for('show_categories'))
    else:
        return render_template('newCountry.html')


# Add a new city
@app.route('/cities/new/', methods=['GET', 'POST'])
def add_city():
    if request.method == 'POST':
        country = session.query(Country).filter(
            Country.name == request.form['country']).first()
        new_city = CatalogItem(name=request.form['name'],
                               description=request.form['description'],
                               last_update=datetime.now(),
                               country=country)
        session.add(new_city)
        session.commit()
        return redirect(url_for('show_categories'))
    else:
        countries = session.query(Country).all()
        return render_template('newCity.html', countries=countries)


@app.route('/clearSession')
def clear_session():
    login_session.clear()
    return "Session cleared"


if __name__ == '__main__':
    app.secret_key = 'travel_log_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
