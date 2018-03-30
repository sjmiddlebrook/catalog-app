# Item Catalog Project
Project using Flask application that reads from a database. The website allows users to login using their Google
account information. Once a user is logged in they can add cities and countries to the travel catalog.
The project also includes JSON endpoints for country and city information.

## Dependencies/Pre-requisites
The project uses: 
* The vagrant setup found in [Udacity Fullstack Nanodegree VM](https://github.com/udacity/fullstack-nanodegree-vm). 
* Flask
* SQLAlchemy

## Setup
Run `python3 database_setup.py` to initialize the database.

Run `python3 initialize_categories.py` to insert initial values in the database.

Run `python3 application.py` to run the flask application.



