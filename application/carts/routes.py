from flask import redirect, render_template, url_for, flash, request, session, current_app

from application import db, app
from application.products.models import Addproduct
from application.products.routes import brands, categories





################################ Merge Dictionaries ################################ 
def mergeDicts(dict1, dict2):
    if isinstance(dict1, list) and isinstance(dict2, list):
        return dict1 + dict2
    elif isinstance(dict1, dict) and isinstance(dict2, dict):
        return dict(list(dict1.items()) + list(dict2.items()))
    return False


################################ Add products to the cart ################################ 
@app.route('/addcart', methods=['POST'])
def addCart():
    try:
        product_id = request.form.get('product_id')
        quantity = request.form.get('quantity')
        colors = request.form.get('colors')
        product = Addproduct.query.filter_by(id=product_id).first()
        if product_id and quantity and colors and request.method == "POST":
            DictItems= {product_id: {'name': product.name,
                                    'price': product.price,
                                    'discount': product.discount,
                                    'color': colors,
                                    'quantity': int(quantity),
                                    'image': product.image_1,
                                    'colors': product.colors}}
            if 'Shoppingcart' in session:
                if product_id in session['Shoppingcart']:
                    for key, item in session['Shoppingcart'].items():
                        if int(key) == int(product_id):
                            session.modified = True
                            item['quantity'] += 1
                else:
                    session['Shoppingcart'] = mergeDicts(session['Shoppingcart'], DictItems)
                    return redirect(request.referrer)
            else:
                session['Shoppingcart'] = DictItems
                return redirect(request.referrer)
    except Exception as e:
        print(e)
    finally:
        return redirect(request.referrer)
    

################################ Show Shoppingcart ################################
@app.route('/carts')
def get_cart():
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return redirect(url_for('home'))
    subtotal = 0
    for key, product in session['Shoppingcart'].items():
        discount = (product['discount']/100) * float(product['price'])
        subtotal += int(product['quantity']) * (float(product['price']) - float(discount))
    grandtotal = subtotal
    return render_template('products/carts.html', grandtotal = grandtotal, brands=brands(), categories=categories())


################################ Update item details in shoppingcart(quantity, color) ################################
@app.route('/updatecart/<int:code>', methods=["POST"])
def updatecart(code):
    if 'Shoppingcart' not in session and len(session['Shoppingcart'] <= 0):
        return redirect(url_for('home'))
    if request.method == "POST":
        quantity = request.form.get('quantity')
        color = request.form.get('color')
        try:
            session.modified = True
            for key, item in session['Shoppingcart'].items():
                if int(key) == code:
                    product = Addproduct.query.get_or_404(code)
                    if product.stock >= int(quantity):
                        item['quantity'] = quantity
                        item['color'] = color
                    else:
                        flash(f'Update product details failed! We have {product.name} only {product.stock} pieces in stock!', 'danger')
                        return redirect(url_for(get_cart))
            flash('Product details are updated!', 'success')
            return redirect(url_for(get_cart))
        except Exception as e:
            print(e)
            return redirect(url_for('get_cart'))
    return redirect(url_for('get_cart'))

################################ Delete item from Shoppingcart ################################
@app.route('/deleteitem/<int:id>')
def deleteitem(id):
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return redirect(url_for('home'))
    try:
        session.modified= True
        for key, item in session['Shoppingcart'].items():
            if int(key) == id:
                session['Shoppingcart'].pop(key, None)
        return redirect(url_for('get_cart'))
    except Exception as e:
        print(e)
        return redirect(url_for('get_cart'))


################################ Clear Shoppingcart ################################
@app.route('/clearcart')
def clearcart():
    try:
        session.pop('Shoppingcart', None)
        return redirect(url_for('home'))
    except Exception as e:
        print(e)
