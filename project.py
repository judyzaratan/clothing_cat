from flask import Flask, render_template, url_for, request, redirect,\
    flash, jsonify

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
    item_query = session.query(Item).filter_by(id=item_id).one()
    prev_name = item_query.name
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
    if request.method == 'POST':
        newItem = Item(name=request.form['name'],
                       description=request.form['description'],
                       category_id=int(request.form['category_id']))
        session.add(newItem)
        session.commit()
        return redirect(url_for('catalogCategories'))
    if request.method == 'GET':
        categories = session.query(Category)
        return render_template('addItem.html', categories=categories)


@app.route('/catalog/delete/<int:item_id>', methods=['GET', 'POST'])
def deleteItem(item_id):
    if request.method == 'GET':
        item_to_delete = session.query(Item).filter_by(id=item_id).one()
        return render_template('deleteItem.html', item=item_to_delete)
    if request.method == 'POST':
        item_to_delete = session.query(Item).filter_by(id=item_id).one()
        session.delete(item_to_delete)
        return redirect(url_for('catalogCategories'))


# If not used as an imported module run following code
if __name__ == '__main__':
    # Server reload on code changes
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
