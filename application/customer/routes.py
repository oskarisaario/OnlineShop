from flask import redirect, render_template, url_for, flash, request, session, current_app, make_response, Response
from flask_login import login_required, current_user, login_user, logout_user
import pdfkit
import stripe
#import wkhtmltopdf
from application import db, app, photos, search, bcrypt, login_manager
from .forms import CustomerRegisterForm, CustomerLoginForm
from .models import Customer, CustomerOrder

import secrets
import os



publishable_key = 'pk_test_51NsKcqBQQM3gMqIDpttH1xWgVlQszJrs2YR48aZh3asBfJ7djW0ClxBF1JfmtBEsv81cc5dLHxemYoE0zsFPkp1D007Wtf7yij'
stripe.api_key = 'sk_test_51NsKcqBQQM3gMqIDr8mO3sjgoTXbppQTYmLBXazFHxtLYVT7uW8U6qNJEYd4JvfKpK1c9HY5Jk5EYBszzLghxwg500M5zuo4n8'
#stripe_key = 'sk_test_51NsKcqBQQM3gMqIDr8mO3sjgoTXbppQTYmLBXazFHxtLYVT7uW8U6qNJEYd4JvfKpK1c9HY5Jk5EYBszzLghxwg500M5zuo4n8'
@app.route('/payment', methods=['POST'])
@login_required
def payment():
    invoice = request.form.get('invoice')
    amount = request.form.get('amount')
    print(amount)
    customer = stripe.Customer.create(
        email = request.form['stripeEmail'],
        source = request.form['stripeToken']
    )

    charge = stripe.Charge.create(
        customer = customer.id,
        description = 'Onlineshop',
        amount = amount,
        currency = 'eur'
    )
    orders = CustomerOrder.query.filter_by(customer_id=current_user.id, invoice=invoice).order_by(CustomerOrder.id.desc()).first()
    orders.status = 'Paid'
    db.session.commit()
    return redirect(url_for('paymentSuccess'))


@app.route('/paymentSuccess')
def paymentSuccess():
    return render_template('customer/paymentSuccess.html')



################################### Create customer user and add it to database ################################### 
@app.route('/customer/register', methods=['GET', 'POST'])
def customer_register():
    form = CustomerRegisterForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf8')
        customer = Customer(
            name = form.name.data,
            username = form.username.data,
            email = form.email.data,
            contact = form.contact.data,
            password = hash_password,
            country = form.country.data,
            city = form.city.data,
            address = form.address.data,
            zipcode = form.zipcode.data
        )
        db.session.add(customer)
        flash(f'Registered as {form.username.data}, Welcome!', 'success')
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('customer/register.html', form=form)


###################################  Customer login for shop ################################### 
@app.route('/customer/login', methods=['GET', 'POST'])
def customerLogin():
    form = CustomerLoginForm()
    if form.validate_on_submit():
        user = Customer.query.filter_by(username = form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('You are logged in', 'success')
            next = request.args.get('next')
            return redirect(next or url_for('home'))
        
        flash('Invalid username and/or password!', 'danger')
        return redirect(url_for('customerLogin'))

    return render_template('/customer/login.html', form=form)


################################### Customer logout from shop ################################### 
@app.route('/customer/logout')
def customerLogout():
    logout_user()
    return redirect(url_for('home'))


################################### Route for clicking "Check out" in cart and sends order ################################### 
@app.route('/getOrder')
@login_required
def getOrder():
    if current_user.is_authenticated:
        customer_id = current_user.id
        invoice = secrets.token_hex(5)
        try:
            order = CustomerOrder(invoice=invoice, customer_id=customer_id, orders = session['Shoppingcart'])
            db.session.add(order)
            db.session.commit()
            session.pop('Shoppingcart')
            flash('Your order has been sent', 'success')
            return redirect(url_for('orders', invoice=invoice))
        
        except Exception as e:
            print(e)
            flash('Something went wrong with order', 'danger')
            return redirect(url_for('get_cart'))
    
    flash('Please login before proceed!', 'danger')
    return redirect(url_for('customerLogin'))


################################### Route for invoice page. Count up prices of products in CustomerOrder ################################### 
@app.route('/orders/<invoice>')
@login_required
def orders(invoice):
    if current_user.is_authenticated:
        grandTotal = 0
        subTotal = 0
        customer_id = current_user.id
        customer = Customer.query.filter_by(id=customer_id).first()
        orders = CustomerOrder.query.filter_by(customer_id=customer_id, invoice=invoice).order_by(CustomerOrder.id.desc()).first()
        for _key, product in orders.orders.items():
            discount = (product['discount']/100) * float(product['price'])
            subTotal = int(product['quantity']) * (float(product['price']) - discount)
            grandTotal += subTotal   
    else:
        flash('Please login before proceed!', 'danger')
        return redirect(url_for('customerLogin'))
    
    return render_template('/customer/order.html', invoice=invoice, subTotal=subTotal, grandTotal=grandTotal, customer=customer, orders=orders)


################################### Route for getting PDF receipt ################################### 
@app.route('/get_pdf/<invoice>', methods=['POST'])
@login_required
def get_pdf(invoice):
    if current_user.is_authenticated:
        grandTotal = 0
        subTotal = 0
        customer_id = current_user.id
        if request.method == "POST":
            customer = Customer.query.filter_by(id=customer_id).first()
            orders = CustomerOrder.query.filter_by(customer_id=customer_id).order_by(CustomerOrder.id.desc()).first()
            for _key, product in orders.orders.items():
                discount = (product['discount']/100) * float(product['price'])
                subTotal = int(product['quantity']) * (float(product['price']) - discount)
                grandTotal += subTotal   

            #grandTotal = str(grandTotal)
            rendered = render_template('/customer/pdf.html', invoice=invoice, grandTotal=grandTotal, customer=customer, orders=orders)
            path_wkhtmltopdf = "C:\Program Files\wkhtmltopdf\\bin\wkhtmltopdf.exe"
            config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
            pdf = pdfkit.from_string(rendered, False,configuration=config)
            response = make_response(pdf)
            response.headers['content-Type'] = 'application/pdf'
            response.headers['content-Disposition'] = 'inline: filename='+invoice+'.pdf'
            return response
    
    return request(url_for('orders'))