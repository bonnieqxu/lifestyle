from app import app
from flask import render_template, request, redirect, url_for, session, flash
import re
from datetime import datetime, timedelta, date
import mysql.connector
import app.connect as connect
from app.utility import logged_in
from app.forms import RegistrationForm  
import re
import os
import uuid  

# Create an instance of hashing
from flask_hashing import Hashing

hashing = Hashing(app)

# Function to establish database connection and return cursor
def getCursor():
    connection = mysql.connector.connect(
        user=connect.dbuser,
        password=connect.dbpass,
        host=connect.dbhost,
        auth_plugin='mysql_native_password',
        database=connect.dbname,
        autocommit=True
    )
    dbconn = connection.cursor()
    return dbconn, connection

def closeConnection(cursor, connection):
    cursor.close()
    connection.close()

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        userrole = 'MM'  # default role to member

        title = form.title.data
        firstname = form.firstname.data
        lastname = form.lastname.data
        position = form.position.data
        phone = form.phone.data
        email = form.email.data
        address = form.address.data
        dob = form.dob.data
        status = 'A'  # default for Active user

        cursor, connection = getCursor()
        cursor.execute('SELECT * FROM user WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only letters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        elif (datetime.now().date() - dob).days < 18*365: # Checking if user is at least 18 years old
            msg = 'You must be 18 years old or above to register!'
        else:
            hashed = hashing.hash_value(password, salt='abcd')
            cursor.execute('INSERT INTO user (username, passwordhash, userrole, status) VALUES (%s, %s, %s, %s)',
                            (username, hashed, userrole, status,))
            connection.commit()

            GID = cursor.lastrowid #retrieve the ID from lastrowid to be used as member_ID 

            cursor.execute('INSERT INTO member VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', 
                           (GID, title, firstname, lastname, position, phone, email, address, dob, None, None, None))
            connection.commit()

            # Execute the additional query to fetch subscription information
            sql = """SELECT
                    (SELECT subscription_cost FROM subscription WHERE subscription_type = 'M') AS MonthlySubFee,
                    (SELECT subscription_discount FROM subscription WHERE subscription_type = 'M') AS MonthlySubDiscount,
                    (SELECT subscription_cost FROM subscription WHERE subscription_type = 'Y') AS AnnualSubFee,
                    (SELECT subscription_discount FROM subscription WHERE subscription_type = 'Y') AS AnnualSubDiscount;"""
            cursor.execute(sql)
            result = cursor.fetchone()

            session['MonthlySubFee'] = float(result[0])
            session['MonthlySubDiscount'] = float(result[1])
            session['AnnualSubFee'] = float(result[2])
            session['AnnualSubDiscount'] = float(result[3])
            # (LINE78-90) The above session values are not being used in javascript - javascript still hard coded
            # the float() function is not changing session values - they are still strings
            # need to use parseInt/parseFloat in javascript to convert them
            
            flash(f'Account created successfully for {form.username.data}', category='success')
            closeConnection(cursor, connection)

            session['GID'] = GID
            return render_template('payment_form.html')

    return render_template('register.html', form=form, msg=msg)


# payment
@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if request.method == 'POST':
        # obtain info from form
        subscription_type = request.form.get('subscriptionType')
        subscription_cost_with_symbol = request.form.get('amountDue')
        subscription_cost = float(subscription_cost_with_symbol.replace('$', ''))

        # obtain saved GID value
        GID = session.get('GID')

         # Connect to MySQL database      
        cursor, connection = getCursor()

        # Execute the SQL query to get the member_id using GID
        cursor.execute("SELECT * FROM member WHERE member_id = %s", (GID,))
        member_id = cursor.fetchone()[0]

        # calculate payment date
        payment_date = datetime.now().strftime('%Y-%m-%d')
    
        # Calculate expiry date
        current_date = datetime.now().date()  # real date
        if subscription_type == 'annual':
            subscription_type_abbr = 'Y'
            payment_subscription_id = 2
            expiry_date = current_date + timedelta(days=365)
        elif subscription_type == 'monthly':
            subscription_type_abbr = 'M'
            payment_subscription_id = 1
            expiry_date = current_date + timedelta(days=30)
        
        # insert data into member table
        sql_member = """UPDATE member
                SET member_subscription_type = %s, member_subscription_expiry_date = %s
                WHERE member_id = %s"""
        parameters_member = (subscription_type_abbr, expiry_date, member_id)
        cursor.execute(sql_member,parameters_member)

        # insert data into payment table
        sql_payment = """INSERT INTO payment (payment_type, payment_workshop_id, 
        payment_lesson_id, payment_subscription_id, payment_date, payment_payor_id, payment_amount) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        parameters_payment = ('C', None, None, payment_subscription_id, payment_date, member_id, subscription_cost)
        cursor.execute(sql_payment, parameters_payment)

        connection.commit()
        closeConnection(cursor, connection)

        return render_template('payment_successful.html', subscription_type=subscription_type, expiry_date=expiry_date, subscription_cost=subscription_cost)
    return render_template('payment_form.html')


@app.route('/payment_successful')
def payment_successful():
    return render_template('payment_successful.html')

