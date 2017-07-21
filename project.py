from flask import Flask, render_template, url_for, request, redirect, flash, jsonify


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item

app = Flask(__name__)
# Create an instance of the Flask class with name of running application
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Following function called HELLO world will be executed if any calls from the
# server have the route of / or /hello
@app.route('/')
def catalogCategories():
    catalog = session.query(Category)
    items = session.query(Item)
    for item in items:
        print item.name, item.category.name
    for item in catalog:
        print item.name
    return render_template('catalog.html')


# If not used as an imported module run following code
if __name__ == '__main__':
    # Server reload on code changes
    app.debug = True
    #
    app.run(host='0.0.0.0', port=5000)
