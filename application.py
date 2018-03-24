from flask import Flask, render_template, request, redirect, jsonify, url_for
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Country, CatalogItem

app = Flask(__name__)

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/hello')
def hello_world():
    return 'Hello, Test!'


@app.route('/countries/<int:country_id>/JSON')
def countries_json(country_id):
    country = session.query(Country).filter_by(id=country_id).one()
    return jsonify(Country=country.serialize)


@app.route('/countries/<int:country_id>/cities/JSON')
def country_cities_json(country_id):
    country = session.query(Country).filter_by(id=country_id).one()
    cities = session.query(CatalogItem).filter_by(
        country_id=country_id).all()
    return jsonify(Cities=[i.serialize for i in cities])


# Show all categories
@app.route('/countries/')
def show_categories():
    countries = session.query(Country).all()
    city_catalog_items = session.query(CatalogItem).order_by(desc(CatalogItem.last_update)).all()
    # return "This page will show all my restaurants"
    return render_template('countries.html', countries=countries,
        items=city_catalog_items)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
