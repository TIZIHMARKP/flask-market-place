
from market import app, db
from flask import render_template, redirect, url_for, flash, request, abort
from market.models import Item, User
from market.forms import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm, DeleteItemForm, CreateItemForm, UpdateItemForm
from market import db
from flask_login import login_user, logout_user, login_required, current_user



# ===================  Helper function to check if current user is admin =============
def admin_required():
    
    if not current_user.is_authenticated or not current_user.is_admin:
        flash('Sorry you need admin privileg to access this page', category='danger')
        abort(403)  # Forbidden


# =================== PUBLIC ROUTES =======================
@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/market', methods = ['GET', 'POST'])
@login_required                # to take our users to the login page
def market_page():
    purchase_form = PurchaseItemForm()
    selling_form = SellItemForm()

    # if purchase_form.validate_on_submit():
    #     print(request.form.get('purchased_item'))    # to know which item our user tried to purchased

    if request.method == "POST":
        # Purchase item logic
        purchased_item = request.form.get('purchased_item')
        p_item_object = Item.query.filter_by(name = purchased_item).first()

        if p_item_object:
            if current_user.can_purchase(p_item_object):
                p_item_object.buy(current_user)           # can buy method in Item models
                
                flash(f"Congratulations. You purchased {p_item_object.name} for {p_item_object.price}$", category = 'success')
            else:
                flash(f"Unfortunately, you don't have neough money to purchase {p_item_object.name}", category = 'danger')

        # Sell Item logic
        # sold_item = request.form.get('sold_item')
        # s_item_object = Item.query.filter_by(name = sold_item).first()
        # if s_item_object:
        #     if current_user.can_sell(s_item_object):     # can_sell method in Item models
        #         s_item_object.sell(current_user)

        #         flash(f"Congratulations. You sold {s_item_object.name} back to market {s_item_object.price}$", category = 'success')

        #     else:
        #         flash(f"Something went wrong with selling {s_item_object.name}", category = 'danger')

        #         pass

        # market/routes.py - More explicit selling logic

        # Sell Item logic
        if request.method == "POST":
            
            sold_item = request.form.get('sold_item')
            s_item_object = Item.query.filter_by(name=sold_item).first()
            
            if s_item_object:
                
                print(f"Item: {s_item_object.name}, Current Owner: {s_item_object.owner}, User ID: {current_user.id}") # Debugging
                
                if current_user.can_sell(s_item_object):
                    
                    s_item_object.owner = None  # Setting owner to none directly. 
                    current_user.budget += s_item_object.price  # Updating budget
                    
                    db.session.commit()
                    
                    # Verify the change
                    db.session.refresh(s_item_object)
                    print(f"After sell, Item: {s_item_object.name}, Owner: {s_item_object.owner}")
                    
                    flash(f"Congratulations You have sold {s_item_object.name} back to market for ${s_item_object.price}", category='success')
                else:
                    flash(f"Something went wrong with selling {s_item_object.name}", category='danger')

    
        return redirect(url_for('market_page'))


    if request.method == "GET":         # removing the form resubmision output 
        items = Item.query.filter_by(owner = None ).all()     # filtering user puchased item, to makesure its no longer idsplayed

        owned_items = Item.query.filter_by(owner = current_user.id).all() 

        return render_template('market.html', items=items, purchase_form = purchase_form, owned_items = owned_items, selling_form = selling_form)

@app.route('/register', methods = ['GET', 'POST'])
def register_page():
    form = RegisterForm()

    if form.validate_on_submit():
        # creating new user
        user_to_create = User(username = form.username.data,
                              email_address = form.email_address.data,
                              password = form.password1.data
                              )

        db.session.add(user_to_create)
        db.session.commit()

        # checking if the user is the first user so as to make them as an admin
        if User.query.count() == 1:
            user_to_create.is_admin = True
            db.session.commit()
            flash(f'You have been granted admin privileges as the first user', category='info')

        login_user(user_to_create)
        flash(f'Account created successfully. You ar enow logged in as {user_to_create.username}', category = 'success')
        
        return redirect(url_for('market_page'))

    if form.errors != {}:   # if there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f"There was an error with creating a user: {err_msg}", category = 'danger')


    return render_template('register.html', form = form)


@app.route('/login', methods = ['GET', 'POST'])
def login_page():

    form = LoginForm()

    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username = form.username.data).first()

        if attempted_user and attempted_user.check_password_correction(
            attempted_password = form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success login as: {attempted_user.username}', category = 'success')

            if attempted_user.is_admin:  # checking if attempted logging user is an admin
                flash(f'You are logged in as ADMIN', category='info')

            return redirect(url_for('market_page'))

        else: 
            flash('Username and Password Incorrect', category='danger')


    return render_template('login.html', form = form)


@app.route('/logout', methods = ['GET', 'POST'])
def logout_page():

    logout_user()

    flash("You have been logged out", category='info')

    return redirect(url_for('home_page'))


# ==================== ADMIN CRUD ROUTES OPERATIONSs ====================
@app.route('/admin/items', methods=['GET'])
@login_required
def admin_items_page(): # Admin page to view all items in the system which shows all the items regardless of ownership
    # Checking if user is admin
    if not current_user.is_admin:
        flash('You are not permitted to access this page', category='danger')
        return redirect(url_for('market_page'))
    
    all_items = Item.query.all()  # reading all items from database
    
    delete_form = DeleteItemForm() # Creating forms for different actions
    
    return render_template(
        'admin_items.html',
        items=all_items,
        delete_form=delete_form
    )

    pass 


@app.route('/admin/items/create', methods=['GET', 'POST'])
@login_required
def create_item_page():   # Admin route to create a new item
    
    if not current_user.is_admin:
        flash('You are not permitted to access this page', category='danger')
        return redirect(url_for('market_page'))
    
    form = CreateItemForm()
    
    if form.validate_on_submit():
        try:
            # Creating new item
            new_item = Item(
                name=form.name.data,
                price=form.price.data,
                barcode=form.barcode.data,
                description=form.description.data,
                owner=None  # no owner since everyone can purchase item
            )
            
            db.session.add(new_item)
            db.session.commit()
            
            flash(f"item '{new_item.name}' created successfully", category='success')
            return redirect(url_for('admin_items_page'))
            
        except Exception as e:
            db.session.rollback()
            flash(f"There was an error creating item: {str(e)}", category='danger')
    
    if form.errors:
        for error_list in form.errors.values():
            for error in error_list:
                flash(f"{error}", category='danger')
    
    return render_template('create_item.html', form=form)


@app.route('/admin/items/update/<int:item_id>', methods=['GET', 'POST'])
@login_required
def update_item_page(item_id):  # Admin page to update an existing item
    
    if not current_user.is_admin:
        flash('You are not permitted to access this page', category='danger')
        return redirect(url_for('market_page'))
    
    item_to_update = Item.query.get_or_404(item_id)  # finding the item by its ID
    
    form = UpdateItemForm()
    
    if request.method == 'GET':  # If it's a GET request we populate the form with current data
        form.name.data = item_to_update.name
        form.price.data = item_to_update.price
        form.barcode.data = item_to_update.barcode
        form.description.data = item_to_update.description
    
    if form.validate_on_submit():   # If the form is submitted and valid
        try: # Updating the item fiels
            item_to_update.name = form.name.data
            item_to_update.price = form.price.data
            item_to_update.barcode = form.barcode.data
            item_to_update.description = form.description.data
            
            db.session.commit()
            
            flash(f"The item '{item_to_update.name}' was updated successfully", category='success')
            return redirect(url_for('admin_items_page'))
            
        except Exception as e:
            db.session.rollback()
            flash(f"There was an error updating item: {str(e)}", category='danger')
    
    if form.errors:
        for error_list in form.errors.values():
            for error in error_list:
                flash(f"{error}", category='danger')
    
    return render_template('update_item.html', form=form, item=item_to_update)


@app.route('/admin/items/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):  # Admin route to delete an item
    
    if not current_user.is_admin:
        flash('You are not permitted to access this page', category='danger')
        return redirect(url_for('market_page'))
    
    item_to_delete = Item.query.get_or_404(item_id)
    
    try:
        item_name = item_to_delete.name
        
        if item_to_delete.owner is not None:  # checking if item is owned by someone
            flash(f"Cannot delete '{item_name}' because it is owned by a user. Please sell it first", category='warning')
            return redirect(url_for('admin_items_page'))
        
        db.session.delete(item_to_delete)
        db.session.commit()
        
        flash(f"The item '{item_name}' was deleted successfully", category='success')
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting item: {str(e)}", category='danger')
    
    return redirect(url_for('admin_items_page'))

