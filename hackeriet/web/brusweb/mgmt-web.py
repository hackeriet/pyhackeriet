from flask import Flask, request, Response, render_template, g, redirect, url_for, send_file, jsonify
from functools import wraps
import brusdb as users
import stripe
import os
import uuid
import json

stripe_keys = {
    'secret_key': os.environ['SECRET_KEY'],
    'publishable_key': os.environ['PUBLISHABLE_KEY']
}

stripe.api_key = stripe_keys['secret_key']

app = Flask(__name__)

def check_auth(username, password):
    return users.authenticate(username, password)

def check_admin(username, password):
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

def machine_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not users.authenticate_machine(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


@app.route("/")
def hello():
    return redirect(url_for('index'))

@app.route("/brus/sales.json")
def stats():
    r = []
#    st = users.get_outgoing_transactions()
#    for d in {e for (t,v,e) in st}:
#        if len([t for (t,v,e) in st if e==d]) > 4:
#            r += [{"key": d, "values": [[int(t)*1000,-v] if e==d else [int(t)*1000,0] for (t,v,e) in st]}]
    return json.dumps(r)

@app.route('/brus/')
def index():
    return render_template('index.html')

@app.route("/brus/account")
@requires_auth
def account():
    user=request.authorization.username
    return render_template('account.html', username=user, history=users.transaction_history(user), balance=users.balance(user), key=stripe_keys['publishable_key'])

@app.route("/brus/change-pw", methods=['POST'])
def change_pw():
    user=request.authorization.username
    if check_auth(user, request.form['old']) and request.form['new'] == request.form["new2"]:
        users.set_password(user, request.form["new"])
        return "Success"
    else:
       return "Failure"

@app.route("/brus/withdraw", methods=['POST'])
def manual_subtract():
    user=request.authorization.username
    if users.subtract_funds(user, int(request.form['value']), request.form['desc'], True):
        return redirect(url_for('account'))
    else:
        return "Insufficient funds"

@app.route("/brus/admin")
@requires_admin
def admin():
    user=request.authorization.username
    return render_template('admin.html', username=user, users=users.list_users())

@app.route("/brus/admin/add", methods=['POST'])
@requires_admin
def admin_add():
    users.add_funds(request.form['user'], int(request.form['value']), request.form['desc'])
    return 'ok'

@app.route("/brus/admin/add_user", methods=['POST'])
@requires_admin
def admin_add_user():
    users.add_user(request.form['username'], request.form['realname'], request.form['phone'], request.form['email'], request.form['address'])
    data = uuid.uuid4()
    users.update_card_data(request.form['username'], data.bytes)
    users.reset_password(request.form['username'])
    return "User %s added with card info: '%s'" % (request.form['username'], data.hex)

@app.route("/brus/admin/door.db")
@requires_admin
def backup():
    return send_file("/opt/nfcd/door.db")

@app.route("/brus/charge", methods=['POST'])
@requires_auth
def charge():
    # Amount in cents
    amount = request.form['amountt']
    user=request.authorization.username

    stripe_id = users.get_stripe_id(user)

    if not stripe_id:
        customer = stripe.Customer.create(
            email=users.get_email(user),
            card=request.form['stripeToken']
        )
        stripe_id = customer.id
        users.set_stripe_id(user, stripe_id)

    charge = stripe.Charge.create(
        customer=stripe_id,
        amount=amount,
        currency='NOK',
        description='Hackeriet'
    )

    users.add_funds(user, int(amount)/100, "Transfer with Stripe.")

    return render_template('charge.html', amount=int(amount)/100)


@app.route("/brus/machine/sell")
@machine_auth
def sell():
    mid = request.authorization.username
    slot = request.args.get("slot", '')
    card_data = request.args.get("card", '')

    price, desc = users.get_product_price_descr(users.getproduct(mid, slot))

    if users.subtract_funds_card(card_data, price, desc):
        return Response('Accepted\n',202)
    return Response('Payment Required\n',402)

if __name__ == "__main__":
    app.debug = False
    app.run()
