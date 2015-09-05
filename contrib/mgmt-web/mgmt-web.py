from flask import Flask, request, Response, render_template, g, redirect, url_for
from functools import wraps
from hackeriet.users import Users
import stripe
import os

stripe_keys = {
    'secret_key': os.environ['SECRET_KEY'],
    'publishable_key': os.environ['PUBLISHABLE_KEY']
}

stripe.api_key = stripe_keys['secret_key']

app = Flask(__name__)

def get_users():
    users = getattr(g, '_users', None)
    if users is None:
        users = g._users = Users()
    return users

@app.teardown_appcontext
def close_connection(exception):
    users = getattr(g, '_users', None)
    if users is not None:
        users.db.close()

def check_auth(username, password):
    users = get_users()
    return users.authenticate(username, password)

def check_admin(username, password):
    users = get_users()
    return users.authenticate_admin(username, password)

def authenticate():
    return Response('L33t hax0rz only\n',401,{'WWW-Authenticate': 'Basic realm="Hackeriet"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def requires_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_admin(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route("/")
def hello():
    return "Goodbye World!"

@app.route("/brus/account")
@requires_auth
def account():
    users = get_users()
    user=request.authorization.username
    return render_template('account.html', username=user, history=users.transaction_history(user), balance=users.balance(user), key=stripe_keys['publishable_key'])

@app.route("/brus/change-pw", methods=['POST'])
def change_pw():
    user=request.authorization.username
    if check_auth(user, request.form['old']) and request.form['new'] == request.form["new2"]:
        users = get_users()
        users.set_password(user, request.form["new"])
        return "Success"
    else:
       return "Failure"

@app.route("/brus/withdraw", methods=['POST'])
def manual_subtract():
    user=request.authorization.username
    users = get_users()
    if users.subtract_funds(user, int(request.form['value']), request.form['desc']):
        return redirect(url_for('account'))
    else:
        return "Insufficient funds"

@app.route("/brus/admin")
@requires_admin
def admin():
    user=request.authorization.username
    users = get_users()
    return render_template('admin.html', username=user, users=users.list_users())

@app.route("/brus/admin/add", methods=['POST'])
@requires_admin
def admin_add():
    users = get_users()
    users.add_funds(request.form['user'], request.form['value'], request.form['desc'])
    return 'ok'

@app.route("/brus/charge", methods=['POST'])
@requires_auth
def charge():
    # Amount in cents
    amount = request.form['amountt']
    users = get_users()
    user=request.authorization.username

    customer = stripe.Customer.create(
        email=users.get_email(user),
        card=request.form['stripeToken']
    )

    charge = stripe.Charge.create(
        customer=customer.id,
        amount=amount,
        currency='NOK',
        description='Hackeriet'
    )

    users.add_funds(user, int(amount)/100, "Transfer with Stripe.")
    
    return render_template('charge.html', amount=int(amount)/100)


if __name__ == "__main__":
    app.debug = True
    app.run()
