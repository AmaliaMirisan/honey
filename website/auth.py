from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Account, Transactions
from . import db   ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user
from .rsa_encryption import RSA_encrypt, RSA_decrypt, get_public_key
from flask_login import current_user

auth = Blueprint('auth', __name__)

@auth.route('/account', methods=['GET'])
@login_required
def account():
    account = Account.query.filter_by(user_id=current_user.id).first()
    if not account:
        flash("No account information found.", category="error")
        return redirect(url_for('views.home'))

    user_details = {
        'account_number': account.account_number,
        'balance': account.balance,
        'currency': account.currency
    }
    return render_template('user_view_page.html', **user_details)
@auth.context_processor
def inject_user():
    return dict(user=current_user)
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Load private key
        with open("website/private_key.txt", "r") as priv_file:
            n, d = map(int, priv_file.read().split())

        # Verificare pentru utilizatorul sysadmin
        if email == "sysadmin@db" and password == "sysadmin":
            flash('Logged in as admin!', category='success')

            # Creeaza un obiect temporar pentru sysadmin
            class AdminUser:
                is_authenticated = True
                is_active = True
                is_anonymous = False
                id = "sysadmin"
                role = "admin"  # Rol specific pentru sysadmin

                def get_id(self):
                    return self.id

            sysadmin_user = AdminUser()
            login_user(sysadmin_user)
            return redirect(url_for('auth.admin_dashboard'))

        user = User.query.filter_by(email=email).first()
        if user:
            decrypted_password = RSA_decrypt(user.password, n, d)
            print(decrypted_password + " is decrypted")
            if decrypted_password.strip() == password:
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # Load public key
        with open("website/public_key.txt", "r") as pub_file:
            n, e = map(int, pub_file.read().split())

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            encrypted_password = RSA_encrypt(password1, n, e)
            new_user = User(email=email, first_name=first_name, password=encrypted_password)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)


@auth.route('/admin-dashboard', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    # Permite accesul doar pentru sysadmin
    if current_user.id != "sysadmin":
        flash('Access denied!', category='error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        form_type = request.form.get('form_type')  # Verificam ce tip de formular a fost trimis

        if form_type == 'user':
            # Gestionare Create User
            email = request.form.get('email')
            first_name = request.form.get('first_name')
            password = request.form.get('password')

            # Validari pentru campurile formularului Create User
            if not email or len(email) < 4:
                flash('Email must be greater than 3 characters.', category='error')
            elif not first_name or len(first_name) < 2:
                flash('First name must be greater than 1 character.', category='error')
            elif not password or len(password) < 7:
                flash('Password must be at least 7 characters.', category='error')
            else:
                encrypted_password = RSA_encrypt(password, *get_public_key())
                new_user = User(email=email, first_name=first_name, password=encrypted_password)
                db.session.add(new_user)
                db.session.commit()
                flash('User created successfully!', category='success')

        elif form_type == 'account':
            # Gestionare Create Account
            user_id = request.form.get('user_id')
            balance = request.form.get('balance')
            currency = request.form.get('currency')
            account_number = request.form.get('account_number')

            # Validari pentru campurile formularului Create Account
            if not user_id or not User.query.get(user_id):
                flash('User ID does not exist.', category='error')
            elif not currency or len(currency) != 3:
                flash('Currency must be a 3-letter code.', category='error')
            elif not account_number or len(account_number) < 4:
                flash('Account number must be greater than 3 characters.', category='error')
            elif not balance or float(balance) <= 0:
                flash('Balance must be a positive number.', category='error')
            else:
                new_account = Account(
                    user_id=user_id,
                    balance=float(balance),
                    currency=currency,
                    account_number=account_number
                )
                db.session.add(new_account)
                db.session.commit()
                flash('Account created successfully!', category='success')

    return render_template('admin_dashboard.html')

@auth.route('/create-user', methods=['GET', 'POST'])
@login_required
def create_user():
    if current_user.id != "sysadmin":
        flash('Access denied!', category='error')
        return redirect(url_for('auth.admin_dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password = request.form.get('password')

        # Validare si creare user
        if len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif len(last_name) < 2:
            flash('Last name must be greater than 1 character.', category='error')
        elif len(password) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            encrypted_password = RSA_encrypt(password, *get_public_key())
            new_user = User(email=email, first_name=first_name, last_name=last_name, password=encrypted_password)
            db.session.add(new_user)
            db.session.commit()
            flash('User created successfully!', category='success')
            return redirect(url_for('auth.admin_dashboard'))

    return render_template('create_user.html')


@auth.route('/create-account', methods=['GET', 'POST'])
@login_required
def create_account():
    if current_user.id != "sysadmin":
        flash('Access denied!', category='error')
        return redirect(url_for('auth.admin_dashboard'))

    if request.method == 'POST':
        user_id = request.form.get('user_id')
        balance = request.form.get('balance')
        currency = request.form.get('currency')
        account_number = request.form.get('account_number')

        # Validare si creare cont
        if not User.query.get(user_id):
            flash('User ID does not exist.', category='error')
        elif len(currency) != 3:
            flash('Currency must be a 3-letter code.', category='error')
        elif len(account_number) < 4:
            flash('Account number must be greater than 3 characters.', category='error')
        elif float(balance) <= 0:
            flash('Balance must be positive.', category='error')
        else:
            new_account = Account(
                user_id=user_id,
                balance=float(balance),
                currency=currency,
                account_number=account_number
            )
            db.session.add(new_account)
            db.session.commit()
            flash('Account created successfully!', category='success')
            return redirect(url_for('auth.admin_dashboard'))

    return render_template('create_account.html')

@auth.route('/transaction', methods=['GET', 'POST'])
@login_required
def transaction():
    if request.method == 'POST':
        to_account_id = request.form.get('account_id_to')
        amount = request.form.get('amount')

        # Preluam contul asociat utilizatorului logat
        from_account = Account.query.filter_by(user_id=current_user.id).first()

        # Validare campuri
        if not from_account:
            flash('No account associated with your user ID.', category='error')
            return redirect(url_for('auth.transaction'))

        if not to_account_id or not amount:
            flash('All fields are required!', category='error')
            return redirect(url_for('auth.transaction'))

        try:
            amount = float(amount)
            if amount <= 0:
                flash('Amount must be greater than zero!', category='error')
                return redirect(url_for('auth.transaction'))
        except ValueError:
            flash('Invalid amount!', category='error')
            return redirect(url_for('auth.transaction'))

        # Verificam daca contul destinatar exista
        to_account = Account.query.filter_by(id=to_account_id).first()
        if not to_account:
            flash('Recipient account does not exist!', category='error')
            return redirect(url_for('auth.transaction'))

        # Verificam soldul contului sursa
        if from_account.balance < amount:
            flash('Insufficient balance in your account!', category='error')
            return redirect(url_for('auth.transaction'))

        # Actualizam soldurile conturilor
        from_account.balance -= amount
        to_account.balance += amount

        # Cream tranzactia
        new_transaction = Transactions(
            account_id_from=from_account.id,
            account_id_to=to_account_id,
            amount=amount
        )
        db.session.add(new_transaction)
        db.session.commit()

        flash('Transaction completed successfully!', category='success')
        return redirect(url_for('auth.transaction'))

    return render_template('transaction.html')
