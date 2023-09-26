from flask import redirect, render_template, url_for, flash, request, session, current_app

from application import db, app, photos, search
from .models import Brand, Category, Addproduct
from .forms import Addproducts
import secrets, os




############## Get Brands and Categories for navbar dropmenus #############
def brands():
     brands = Brand.query.join(Addproduct, (Brand.id == Addproduct.brand_id)).all()
     return brands


def categories():
    categories = Category.query.join(Addproduct, (Category.id == Addproduct.category_id)).all()
    return categories


################################################### HANDLING PUBLIC ROUTES ###################################################
@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    products = Addproduct.query.filter(Addproduct.stock > 0).order_by(Addproduct.id.desc()).paginate(page=page, per_page=6)
    return render_template('/products/index.html', products=products, brands=brands(), categories=categories())


#Results for search in navbar
@app.route('/result')
def result():
    searchword = request.args.get('q')
    products = Addproduct.query.msearch(searchword, fields=['name', 'desc'], limit=10)
    return render_template('products/result.html', products=products, brands=brands(), categories=categories())


#View single product
@app.route('/product/<int:id>')
def single_page(id):
    product = Addproduct.query.get_or_404(id)
    return render_template('products/single_page.html', product=product, brands=brands(), categories=categories())


#View products by brand
@app.route('/brand/<int:id>')
def get_brand(id):
    page = request.args.get('page', 1, type=int)
    get_brand = Brand.query.filter_by(id=id).first_or_404()
    brand = Addproduct.query.filter_by(brand=get_brand).paginate(page=page, per_page=3)
    return render_template('/products/index.html', brand=brand, brands=brands(), categories=categories(), get_brand=get_brand)


#View products by category
@app.route('/categories/<int:id>')
def get_category(id):
    page = request.args.get('page', 1, type=int)
    get_cat = Category.query.filter_by(id=id).first_or_404()
    category = Addproduct.query.filter_by(category=get_cat).paginate(page=page, per_page=3)
    return render_template('/products/index.html', category=category, categories=categories(), brands=brands(), get_cat=get_cat)


################################################### BRAND HANDLING ROUTES ###################################################
@app.route('/addbrand', methods=['GET', 'POST'])
def addbrand():
    if 'username' not in session:
        flash('Login required, please login first', 'danger')
        return redirect(url_for('login'))
    if request.method == "POST":
        getbrand = request.form.get('brand')
        brand = Brand(name=getbrand)
        db.session.add(brand)
        flash(f'The Brand {getbrand} was added to your database', 'success')
        db.session.commit()
        return redirect(url_for('admin'))

    return render_template('products/addbrand.html', brands='brands')


@app.route('/updatebrand/<int:id>', methods=['GET', 'POST'])
def updatebrand(id):
    if 'username' not in session:
        flash('Login required, please login first', 'danger')
        return redirect(url_for('login'))
    update_brand = Brand.query.get_or_404(id)
    brand = request.form.get('brand')
    if request.method == 'POST':
        update_brand.name = brand
        flash('Brand has been updated', 'success')
        db.session.commit()
        return redirect(url_for('brands'))
    return render_template('admin/brand.html', title='Update brand', updatebrand = update_brand)


@app.route('/deletebrand/<int:id>', methods=['POST'])
def deletebrand(id):
    brand = Brand.query.get_or_404(id)
    if request.method == "POST":
        try:
            db.session.delete(brand)
            db.session.commit()
            flash(f'Brand: {brand.name} is deleted succesfully', 'success')
            return redirect(url_for('brands'))
        except:
            db.session.rollback()
            flash(f'Error occurred! Brand: {brand.name} was not deleted', 'danger')
            return redirect(url_for('brands'))

    return redirect(url_for('brands'))



################################################### CATEGORY HANDLING ROUTES ###################################################
@app.route('/addcategory', methods=['GET', 'POST'])
def addcategory():
    if 'username' not in session:
        flash('Login required, please login first', 'danger')
        return redirect(url_for('login'))
    if request.method == "POST":
        getbrand = request.form.get('category')
        category = Category(name=getbrand)
        db.session.add(category)
        flash(f'The Category {getbrand} was added to your database', 'success')
        db.session.commit()
        return redirect(url_for('admin'))

    return render_template('products/addbrand.html')


@app.route('/updatecategory/<int:id>', methods=['GET', 'POST'])
def updatecategory(id):
    if 'username' not in session:
        flash('Login required, please login first', 'danger')
        return redirect(url_for('login'))
    update_category = Category.query.get_or_404(id)
    category = request.form.get('category')
    if request.method == 'POST':
        update_category.name = category
        flash('Category has been updated', 'success')
        db.session.commit()
        return redirect(url_for('category'))
    return render_template('admin/brand.html', title='Update category', updatecategory = update_category)


@app.route('/deletecategory/<int:id>', methods=['POST'])
def deletecategory(id):
    category = Category.query.get_or_404(id)
    if request.method == "POST":
        try:
            db.session.delete(category)
            db.session.commit()
            flash(f'Category: {category.name} is deleted succesfully', 'success')
            return redirect(url_for('category'))
        except:
            db.session.rollback()
            flash(f'Error occurred! Category: {category.name} was not deleted', 'danger')
            return redirect(url_for('category'))
        
    return redirect(url_for('admin'))


################################################### PRODUCT HANDLING ROUTES ###################################################
@app.route('/addproduct', methods=['GET', 'POST'])
def addproduct():
    if 'username' not in session:
        flash('Login required, please login first', 'danger')
        return redirect(url_for('login'))
    brands =Brand.query.all()
    categories = Category.query.all()
    form = Addproducts(request.form)
    if request.method == "POST":
        name = form.name.data
        price = form.price.data
        discount = form.discount.data
        stock = form.stock.data
        colors = form.colors.data
        desc = form.description.data
        brand = request.form.get('brand')
        category = request.form.get('category')
        image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
        image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
        image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
        add_product = Addproduct(name=name, price=price, discount=discount, stock=stock, colors=colors, desc=desc, brand_id=brand, category_id=category, image_1=image_1, image_2=image_2, image_3=image_3)
        db.session.add(add_product)
        flash(f'{name} is added to the database', 'success')
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('products/addproduct.html', title='Add Product Page', form = form, brands=brands, categories=categories)


################################################### Update product details ###################################################
@app.route('/updateproduct/<int:id>', methods=['GET', 'POST'])
def updateproduct(id):
    brands = Brand.query.all()
    categories = Category.query.all()
    product = Addproduct.query.get_or_404(id)
    form = Addproducts(request.form)
    brand = request.form.get('brand')
    category = request.form.get('category')
    if request.method == "POST":
        product.name =form.name.data
        product.price = form.price.data
        product.discount = form.discount.data
        product.stock = form.stock.data
        product.brand_id = brand
        product.category_id = category
        product.colors = form.colors.data
        product.desc = form.description.data
        if request.files.get('image_1'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
                product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
            except:
                product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
        if request.files.get('image_2'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
                product.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
            except:
                product.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")       
        if request.files.get('image_3'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))
                product.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
            except:
                product.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
        db.session.commit()
        flash(f'Product: {product.name} is updated', 'success')
        return redirect(url_for('admin'))  
    form.name.data = product.name
    form.price.data = product.price
    form.discount.data = product.discount
    form.stock.data = product.stock
    form.colors.data = product.colors
    form.description.data = product.desc
    return render_template('products/updateproduct.html', form = form, brands = brands, categories = categories, product = product)


@app.route('/deleteproduct/<int:id>', methods=['POST'])
def deleteproduct(id):
    product = Addproduct.query.get_or_404(id)
    if request.method == "POST":
        try:
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))
        except Exception as e:
            print(e)
        db.session.delete(product)
        db.session.commit()

        flash(f'Product: {product.name} deleted succesfully', 'success')
        return redirect(url_for('admin'))
    flash(f'Error occurred! Product: {product.name} is not deleted!', 'danger')
    return redirect(url_for('admin'))
    