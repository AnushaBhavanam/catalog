from flask import Flask, render_template, url_for
from flask import request, redirect, flash, make_response, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Data_Setup import Base, ProductName, ModuleName, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
import datetime

engine = create_engine('sqlite:///fashion.db',
                       connect_args={'check_same_thread': False}, echo=True)
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json',
                            'r').read())['web']['client_id']
APPLICATION_NAME = "Fashion Store"

DBSession = sessionmaker(bind=engine)
session = DBSession()
# Create anti-forgery state token
tbs_cat = session.query(ProductName).all()


# login
@app.route('/login')
def showLogin():

    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    tbs_cat = session.query(ProductName).all()
    tbes = session.query(ModuleName).all()
    return render_template('login.html',
                           STATE=state, tbs_cat=tbs_cat, tbes=tbes)
    # return render_template('myhome.html', STATE=state
    # tbs_cat=tbs_cat,tbes=tbes)


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
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user already connected.'),
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

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px; border-radius: 150px;'
    '-webkit-border-radius: 150px; -moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output


# User Helper Functions
def createUser(login_session):
    User1 = User(name=login_session['username'], email=login_session[
        'email'], picture=login_session['picture'])
    session.add(User1)
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
    except Exception as error:
        print(error)
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session

#####
# Home


@app.route('/')
@app.route('/home')
def home():
    tbs_cat = session.query(ProductName).all()
    return render_template('myhome.html', tbs_cat=tbs_cat)

#####
# Product Category for admins


@app.route('/ProductStore')
def ProductStore():
    try:
        if login_session['username']:
            name = login_session['username']
            tbs_cat = session.query(ProductName).all()
            tbs = session.query(ProductName).all()
            tbes = session.query(ModuleName).all()
            return render_template('myhome.html', tbs_cat=tbs_cat,
                                   tbs=tbs, tbes=tbes, uname=name)
    except:
        return redirect(url_for('showLogin'))

######
# Showing products based on byke category


@app.route('/ProductStore/<int:tbid>/AllItems')
def showProducts(tbid):
    tbs_cat = session.query(ProductName).all()
    tbs = session.query(ProductName).filter_by(id=tbid).one()
    tbes = session.query(ModuleName).filter_by(productnameid=tbid).all()
    try:
        if login_session['username']:
            return render_template('showProducts.html', tbs_cat=tbs_cat,
                                   tbs=tbs, tbes=tbes,
                                   uname=login_session['username'])
    except:
        return render_template('showProducts.html',
                               tbs_cat=tbs_cat, tbs=tbs, tbes=tbes)

#####
# Add New Product


@app.route('/ProductStore/addProductName', methods=['POST', 'GET'])
def addProductName():
    if 'username' not in login_session:
        flash("Please Login First")
        return redirect(url_for('showLogin'))
    if request.method == 'POST':
        company = ProductName(name=request.form['name'],
                              user_id=login_session['user_id'])
        session.add(company)
        session.commit()
        return redirect(url_for('ProductStore'))
    else:
        return render_template('addProductName.html', tbs_cat=tbs_cat)

########
# Edit Product Category


@app.route('/ProductStore/<int:tbid>/edit', methods=['POST', 'GET'])
def editProductCategory(tbid):
    if 'username' not in login_session:
        flash("You cannot edit this Bag Company.")
        return redirect(url_for('showLogin'))
    editProductCategory = session.query(ProductName).filter_by(id=tbid).one()
    creator = getUserInfo(editProductCategory.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot edit this Product Category."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('ProductStore'))
    if request.method == "POST":
        if request.form['name']:
            editProductCategory.name = request.form['name']
        session.add(editProductCategory)
        session.commit()
        flash("Product Category Edited Successfully")
        return redirect(url_for('ProductStore'))
    else:
        # tbs_cat is global variable we can them in entire application
        return render_template('editProductCategory.html',
                               tb=editProductCategory, tbs_cat=tbs_cat)

######
# Delete Product Category


@app.route('/ProductStore/<int:tbid>/delete', methods=['POST', 'GET'])
def deleteProductCategory(tbid):
    if 'username' not in login_session:
        flash("You cannot delete this Bag Company.")
        return redirect(url_for('showLogin'))
    tb = session.query(ProductName).filter_by(id=tbid).one()
    creator = getUserInfo(tb.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot Delete this Product Category."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('ProductStore'))
    if request.method == "POST":
        session.delete(tb)
        session.commit()
        flash("Product Category Deleted Successfully")
        return redirect(url_for('ProductStore'))
    else:
        return render_template(
            'deleteProductCategory.html',
            tb=tb,
            tbs_cat=tbs_cat)

######
# Add New Product Name Details


@app.route('/ProductStore/addItem/addProductDetails/<string:tbname>/add',
           methods=['GET', 'POST'])
def addProductDetails(tbname):
    if 'username' not in login_session:
        flash("Please Login first.")
        return redirect(url_for('showLogin'))
    tbs = session.query(ProductName).filter_by(name=tbname).one()
    # See if the logged in user is not the owner of byke
    creator = getUserInfo(tbs.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't add new product edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showProducts', tbid=tbs.id))
    if request.method == 'POST':
        name = request.form['name']
        rating = request.form['rating']
        color = request.form['color']
        discount = request.form['discount']
        price = request.form['price']
        materialtype = request.form['materialtype']
        productdetails = ModuleName(name=name, rating=rating,
                                    color=color, discount=discount,
                                    price=price,
                                    materialtype=materialtype,
                                    date=datetime.datetime.now(),
                                    productnameid=tbs.id,
                                    user_id=login_session['user_id'])
        session.add(productdetails)
        session.commit()
        return redirect(url_for('showProducts', tbid=tbs.id))
    else:
        return render_template('addProductDetails.html',
                               tbname=tbs.name, tbs_cat=tbs_cat)

######
# Edit Product details


@app.route('/ProductStore/<int:tbid>/<string:tbename>/edit',
           methods=['GET', 'POST'])
def editProduct(tbid, tbename):
    if 'username' not in login_session:
        flash("Please Login first.")
        return redirect(url_for('showLogin'))
    tb = session.query(ProductName).filter_by(id=tbid).one()
    productdetails = session.query(ModuleName).filter_by(name=tbename).one()
    # See if the logged in user is not the owner of byke
    creator = getUserInfo(tb.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't edit this product edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showProducts', tbid=tb.id))
    # POST methods
    if request.method == 'POST':
        productdetails.name = request.form['name']
        productdetails.rating = request.form['rating']
        productdetails.color = request.form['color']
        productdetails.discount = request.form['discount']
        productdetails.price = request.form['price']
        productdetails.materialtype = request.form['materialtype']
        productdetails.date = datetime.datetime.now()
        session.add(productdetails)
        session.commit()
        flash("Product Edited Successfully")
        return redirect(url_for('showProducts', tbid=tbid))
    else:
        return render_template(
            'editProduct.html',
            tbid=tbid,
            productdetails=productdetails,
            tbs_cat=tbs_cat)

#####
# Delte Product Edit


@app.route('/ProductStore/<int:tbid>/<string:tbename>/delete',
           methods=['GET', 'POST'])
def deleteProduct(tbid, tbename):
    if 'username' not in login_session:
        flash("Please Login first.")
        return redirect(url_for('showLogin'))
    tb = session.query(ProductName).filter_by(id=tbid).one()
    productdetails = session.query(ModuleName).filter_by(name=tbename).one()
    # See if the logged in user is not the owner of byke
    creator = getUserInfo(tb.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't delete this product edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showProducts', tbid=tb.id))
    if request.method == "POST":
        session.delete(productdetails)
        session.commit()
        flash("Deleted Product Successfully")
        return redirect(url_for('showProducts', tbid=tbid))
    else:
        return render_template(
            'deleteProduct.html',
            tbid=tbid,
            productdetails=productdetails,
            tbs_cat=tbs_cat)

####
# Logout from current user


@app.route('/logout')
def logout():
    access_token = login_session['access_token']
    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(login_session['username'])
    if access_token is None:
        print('Access Token is None')
        response = make_response(
            json.dumps('Current user not connected....'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = login_session['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = \
        h.request(uri=url, method='POST', body=None, headers={
            'content-type': 'application/x-www-form-urlencoded'})[0]

    print(result['status'])
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(
            json.dumps('Successfully disconnected user..'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("Successful logged out")
        return redirect(url_for('showLogin'))
        # return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Json
'''
Displays all products in all categories

'''


@app.route('/ProductStore/JSON')
def allProductsJSON():
    productcategories = session.query(ProductName).all()
    category_dict = [c.serialize for c in productcategories]
    for c in range(len(category_dict)):
        products = [i.serialize for i in session.query(
            ModuleName).filter_by(productnameid=category_dict[c]["id"]).all()]
        if products:
            category_dict[c]["product"] = products
    return jsonify(ProductName=category_dict)


'''
Displays all the available products details

'''


@app.route('/productStore/productCategories/JSON')
def categoriesJSON():
    products = session.query(ProductName).all()
    return jsonify(productCategories=[c.serialize for c in products])


'''
Displays all the  product  details

'''


@app.route('/productStore/products/JSON')
def itemsJSON():
    items = session.query(ModuleName).all()
    return jsonify(products=[i.serialize for i in items])


'''
Displays all the bags in  specific productcategorie

'''


@app.route('/productStore/<path:product_name>/products/JSON')
def categoryItemsJSON(product_name):
    productCategory = session.query(
        ProductName).filter_by(name=product_name).one()
    products = session.query(ModuleName).filter_by(
        productname=productCategory).all()
    return jsonify(productEdtion=[i.serialize for i in products])


'''
Displays available bags of specific productcompany and required product type

'''


@app.route('/productStore/<path:product_name>/<path:product1_name>/JSON')
def ItemJSON(product_name, product1_name):
    productCategory = session.query(
        ProductName).filter_by(name=product_name).one()
    productEdition = session.query(ModuleName).filter_by(
        name=product1_name, productname=productCategory).one()
    return jsonify(productEdition=[productEdition.serialize])


if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='127.0.0.1', port=8000)
