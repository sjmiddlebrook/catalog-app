from flask import Flask, render_template, request, redirect, jsonify, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CatalogItem

app = Flask(__name__)

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/hello')
def hello_world():
    return 'Hello, Test!'

# Show all categories
@app.route('/categories/')
def showCategories():
    categories = session.query(Category).all()
    # return "This page will show all my restaurants"
    return render_template('categories.html', categories=categories)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
