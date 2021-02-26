from flask import render_template, jsonify, flash, redirect, url_for, request 
from app import app
from app.forms import *
from datetime import datetime
from decimal import *
from app.baltools import *

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = AddressForm()
    if form.validate_on_submit():
        # Ensure ETH address is a string, should add additional testing/checks here later 
        ethaddress = str(form.ethaddress.data)
        # The Graph - ensure ETH address is all lowercase
        ethaddress = ethaddress.lower()
        # pass the ETH address to new route - /ethaddress to pull The Graph Balancer Data 
        return redirect(url_for('ethaddress',ethaddress=ethaddress))
    temp = "Test Data placeholder "

    return render_template('home.html', form=form,testdata=temp)

@app.route('/ethaddress/<ethaddress>', methods=['GET', 'POST'])
def ethaddress(ethaddress):
    # Ensure ETH address is a string, should add additional testing/checks here later 
    ethaddress = str(ethaddress) 
    # The Graph - ensure ETH address is all lowercase
    ethaddress = ethaddress.lower()
    # Test variable to print directly to template output 
    temp = "Test Data placeholder "

    # Collect all digital assets in the wallet
   
    # From wallet holdings, check for BPTs (Balancer Pool Tokens)

    # If BPT found Collect pools the ETH address has 
    results = getBalancer(ethaddress)

    pools = results[0]
    totalrev = results[1]

    return render_template('ethaddress.html', pools=pools,totalrev=totalrev, address=ethaddress, )
