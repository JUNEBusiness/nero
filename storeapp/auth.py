from flask import Blueprint, request, render_template, redirect, url_for, flash, abort
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
import random 


from .forms import RegistrationForm, LoginForm, ProductPostForm, UpdateAccountForm
from .models import User, Product, Cart
from .utils import save_picture, delete_picture, send_reset_email, add_data

auth = Blueprint("auth", __name__)

@auth.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        try:
            if form.picture.data:
                print(form.picture.data)
                picture_file = save_picture(form.picture.data)
                garbage = current_user.image_file
                current_user.image_file = picture_file
                current_user.update()
                if garbage != "default.jpg":
                    delete_picture(garbage)
            current_user.username = form.username.data
            current_user.email = form.email.data
            current_user.update()
            flash('Your account has been updated!', 'success')
        except:
            flash('Something went wrong!', 'danger')
        
        return redirect(url_for('auth.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('profile.html', title='Account',
                           image_file=image_file, form=form)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("views.home"))
    form = LoginForm()
    if request.method == "GET":
        return render_template("login.html", title="Login", form=form)
    elif request.method == "POST":
        if form.validate_on_submit():
            print("Hello! something is wrong if you do not get a bounceback!")
            user = User.query.filter_by(email=form.email.data).first()

            if user and check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                flash("You have been logged in successfully!", "success")
                return redirect(next_page) if next_page else redirect(url_for("views.home"))
            else:
              flash("There is no user with these credentials in our database!", "danger")
              return redirect(url_for("auth.login"))
        else:
            form.email.data=form.email.data
            flash("Incorrect email or password!", "danger")
            return render_template("login.html", title="Login", form=form)


@auth.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    return redirect(url_for("views.home"))


@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("views.home"))
    form = RegistrationForm()
    if request.method == "GET":
        return render_template("customer_register.html", title="Register", form=form)
    elif request.method =="POST":
        if form.validate_on_submit():
            user = User(first_name=form.first_name.data, last_name=form.last_name.data, address=form.address.data, username=form.username.data, email=form.email.data, phone_number=form.phone_number.data, password=generate_password_hash(form.password.data)) 
            user.insert()
            flash(f"Your account has been created! You are now able to log in { form.username.data }", "success")
            return redirect(url_for("auth.login"))
        else:
            form.username.data=form.username.data
            form.email.data=form.email.data
            return render_template("customer_register.html", title="Register", form=form)
        

@auth.route("/admin_registration", methods=["GET", "POST"])
def admin_registration():
    if current_user.is_authenticated:
        return redirect(url_for("views.home"))
    form = RegistrationForm()
    if request.method == "GET":
        return render_template("register.html", title="Register", form=form)
    elif request.method =="POST":
        if form.validate_on_submit():
            user = User(first_name=form.first_name.data, last_name=form.last_name.data, address=form.address.data, username=form.username.data, email=form.email.data, phone_number=form.phone_number.data, password=generate_password_hash(form.password.data), is_admin=True)  
            user.insert()
            flash(f"Your admin account has been created! You are now able to log in { form.username.data }", "success")
            return redirect(url_for("auth.login"))
        else:
            form.username.data=form.username.data
            form.email.data=form.email.data
            return render_template("register.html", title="Register", form=form)


@auth.route("/add_product", methods=["GET", "POST"])
@login_required
def add_product():
    if current_user.is_authenticated:
        form = ProductPostForm()
        if request.method == "GET":
            return render_template("add_product.html", title="Add product", form=form)
        if form.validate_on_submit():
            product = Product(price=form.price.data, product_code= random.randrange(10000, 90000, 1234), name=form.name.data, category=form.category.data, url=form.product_url.data, description="Lorem ipsum dolor sit amet, adipiscing elit.")
            product.insert()
            flash("You have successfully added this product to the marketplace")
            return redirect(url_for("views.home"))
        else:
            return render_template("add_product.html", title="Add product", form=form)
    else:
        abort(403)


@auth.route("/add_to_cart", methods=["POST"])
@login_required
def add_to_cart():
    if current_user.is_authenticated:
        form = ProductPostForm()
        if request.method == "GET":
            return render_template("add_product.html", title="Add product", form=form)
        if form.validate_on_submit():
            product = Product(price=form.price.data, product_code= random.randrange(10000, 90000, 1234), name=form.name.data, category=form.category.data, url=form.product_url.data, description="Lorem ipsum dolor sit amet, adipiscing elit.")
            product.insert()
            flash("You have successfully added this product to the marketplace")
        else:
            return render_template("add_product.html", title="Add product", form=form)
    else:
        abort(403)


@auth.route("/remove_from_cart", methods=["GET"])
@login_required
def remove_from_cart():
    if current_user.is_authenticated:
        form = ProductPostForm()
        if request.method == "GET":
            return render_template("add_product.html", title="Add product", form=form)
        if form.validate_on_submit():
            product = Cart.query.get()
            product.delete()
            flash("You have successfully added this product to the marketplace")
        else:
            return render_template("add_product.html", title="Add product", form=form)
    else:
        abort(403)

@auth.route("/checkout", methods=["GET"])
@login_required
def checkout():
    if current_user.is_authenticated:
        flash(f"Your products have been shipped to {current_user.address}")
        return redirect(url_for("views.home"))
    else:
        abort(403)