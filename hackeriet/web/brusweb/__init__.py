from flask import Flask, request, Response, render_template, g, redirect, url_for, send_file, jsonify
from functools import wraps
import stripe
import os, uuid, json
import brusdb, members
from hackeriet.mqtt import MQTT

# rulle ut på maskin
# teste maskin
# rulle ut brus
# teste brus
# lage bruker for gratis brus
# fikse graf
# sende mail
# Stripe IDS

stripe_keys = {
    'secret_key': os.environ.get('SECRET_KEY', ""),
    'publishable_key': os.environ.get('PUBLISHABLE_KEY', "")
}

stripe.api_key = stripe_keys['secret_key']

app = Flask(__name__)

def mqtt_handler(mosq,obj,msg):
    if msg.topic == "brus/sell":
        args = json.loads(msg.payload.decode())
        authorise_sale(**args)
    if msg.topic == "hackeriet/reload_users":
        members.load()

def check_auth(username, password):
    return members.authenticate(username, password)

def check_admin(username, password):
    return members.authenticate_admin(username, password)

def authenticate():
    return Response('L33t hax0rz only\n',401,
                    {'WWW-Authenticate': 'Basic realm="Hackeriet"'})

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
    return redirect(url_for('index'))

@app.route("/brus/sales.json")
def stats():
    r = []
#    st = brusdb.get_outgoing_transactions()
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
    return render_template('account.html', username=user,
                           history=brusdb.transaction_history(user),
                           balance=brusdb.balance(user),
                           key=stripe_keys['publishable_key'])

@app.route("/brus/withdraw", methods=['POST'])
def manual_subtract():
    user=request.authorization.username
    if brusdb.subtract_funds(user, int(request.form['value']),
                            request.form['desc'], True):
        return redirect(url_for('account'))
    else:
        return "Insufficient funds"

@app.route("/brus/admin")
@requires_admin
def admin():
    user=request.authorization.username
    return render_template('admin.html', username=user,
                           brusdb=members.list_users())

@app.route("/brus/admin/add", methods=['POST'])
@requires_admin
def admin_add():
    brusdb.add_funds(request.form['user'], int(request.form['value']),
                    request.form['desc'])
    return 'ok'

@app.route("/brus/charge", methods=['POST'])
@requires_auth
def charge():
    # Amount in cents
    amount = request.form['amountt']
    user=request.authorization.username

    stripe_id = brusdb.get_stripe_id(user)

    if not stripe_id:
        customer = stripe.Customer.create(
            email=members.get_email(user),
            card=request.form['stripeToken']
        )
        stripe_id = customer.id
        brusdb.set_stripe_id(user, stripe_id)

    charge = stripe.Charge.create(
        customer=stripe_id,
        amount=amount,
        currency='NOK',
        description='Hackeriet'
    )

    brusdb.add_funds(user, int(amount)/100, "Transfer with Stripe.")

    return render_template('charge.html', amount=int(amount)/100)

def authorise_sale(slot, card_data):
    price, desc = brusdb.get_product_price_descr(brusdb.getproduct(mid, slot))

    if brusdb.subtract_funds(members.username_from_card(card_data), price, desc):
        mqtt("brus/dispense", slot)

    mqtt("brus/error", "Insufficient funds")

if __name__ == "__main__":
    main()

def main():
    members.load()
    mqtt = MQTT(mqtt_handler)
    mqtt.subscribe("brus/sell")
    mqtt.subscribe("hackeriet/reload_users")
    app.debug = False
    app.run()
