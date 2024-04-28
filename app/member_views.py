from app import app
from flask import render_template, session, redirect, url_for, request, flash
import mysql.connector
import app.connect as connect
from app.utility import logged_in
from app.forms import EditMemberForm, EditMemberProfileForm, MemberSubscriptionForm
import os, uuid  # For generating unique identifiers
from wtforms import StringField, PasswordField, EmailField, SelectField, DateField, TextAreaField, TimeField
from datetime import datetime, timedelta, date
import re

# Create an instance of hashing
from flask_hashing import Hashing
hashing = Hashing(app)


# Function to establish database connection and return cursor
def getCursor():
    global dbconn
    global connection

    # Establish a database connection using provided credentials
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

# Function to close database connection
def closeConnection(conn_param=None):
    global dbconn
    global connection
    if dbconn:
        dbconn.close()
    if conn_param:
        conn_param.close()
    else:
        # Handle the case when conn_param is None
        pass


# member dashboard
@app.route('/member/home', methods=['GET', 'POST'])
@logged_in
def member_home():
    # Retrieve user_id from session
    user_id = session['id']
    image = None

    # Establish database connection
    cursor, connection = getCursor()

    # Fetch image associated with the logged-in user
    cursor.execute('SELECT * FROM image WHERE user_id = %s', (session['id'],) )
    image_data = cursor.fetchone()

    # Check if image data exists
    if image_data:
        image = image_data[2]

    # Fetch user's full name
    cursor.execute("""SELECT CONCAT(member_title, ' ', member_firstname, ' ', member_familyname) 
                    AS userfullname FROM member WHERE member_id = %s""", (session['id'],))
    userfullname = cursor.fetchone()[0]

    #check the expiry of the user subscription. if it is less than 7 days away, prompt reminder
    #to renew subscription
    cursor.execute("""SELECT * FROM member WHERE member_id = %s 
                   and  DATEDIFF(member_subscription_expiry_date, CURDATE()) <= 7
                    AND DATEDIFF(member_subscription_expiry_date, CURDATE()) >= 0""", (session['id'],))
    reminder_member = cursor.fetchone()

    # Display a flash message if the subscription is expiring soon
    if reminder_member:
        flash('Your subscription is expiring in 7 days or less. Please renew your subscription', category='warning')

    # Close database connection
    closeConnection()

    # Pass image data to the template
    return render_template('member_home.html', user_id=user_id, image=image, userfullname=userfullname,)



# Profile route
@app.route('/member/profile', methods=['GET', 'POST'])
@logged_in
def member_profile():
    # Get the member ID from the session
    member_id = session['id']

    # Initialise variables
    msg=''
    form = EditMemberProfileForm()

    # Handling GET request
    if request.method == 'GET':
        # Establish database connection
        cursor, connection = getCursor()

        # Fetch the user's profile information from the database
        cursor.execute('SELECT * FROM member WHERE member_id = %s', (member_id,) )
        profile = cursor.fetchone()

        # Populate the form fields with profile information
        form.title.data = profile[1]
        form.firstname.data = profile[2]
        form.lastname.data = profile[3]
        membername = profile[2] + ' ' + profile[3]
        form.position.data = profile[4]
        form.phone.data = profile[5]
        form.email.data = profile[6]
        form.address.data = profile[7]
        form.dob.data = profile[8]

        #retrieve member image from image table
        cursor, connection = getCursor()
        cursor.execute('select * from image where user_id = %s', (member_id,))
        imagelist = cursor.fetchall()
        form.images.choices =  [(image[2]) for image in imagelist]

        closeConnection()

        # Render the member profile page with form and member information
        return render_template("member_views.html", form=form, member_id=member_id, membername=membername)
    
  
    # Handling POST request
    elif request.method == 'POST':
        # Validate the form
        if form.validate_on_submit():

            # Extract form data
            title = form.title.data
            firstname = form.firstname.data
            lastname = form.lastname.data
            position = form.position.data
            phone = form.phone.data
            email = form.email.data
            address = form.address.data
            dob = form.dob.data
            
            # Update member profile information in the database
            cursor, connection = getCursor()
            cursor.execute("""UPDATE member SET member_title=%s, member_firstname=%s, member_familyname=%s, 
                            member_position=%s, member_phonenumber=%s, member_email=%s, member_dob=%s,
                            member_address=%s WHERE member_id=%s""",
                            (title, firstname, lastname, position, phone, email, dob, address, member_id))
                
            closeConnection()
        
            uploaded_files = form.images.data

            # Save uploaded files to server and database
            if uploaded_files is not None:
                for idx, file in enumerate(uploaded_files):

                    random_string = str(uuid.uuid4())[:8]  # Using UUID for randomness
                    new_filename = random_string + '_' + file.filename
                    file_path = os.path.join('app', 'static/images', new_filename)
                    file.save(file_path)
                    cursor, connection = getCursor()
                    cursor.execute('INSERT INTO image ( user_id, image) VALUES (%s, %s)', 
                        (member_id, new_filename,))
            
            #logic below is to cater for deleting image
            #retrieve the selected images to be deleted
            #control is a checkbox
            selected_options = request.form.getlist('option')
            
            for option in selected_options:
                imagepath = os.path.join('app', 'static/images', option)
                # Check if the file exists before attempting to delete it
                if os.path.exists(imagepath):
                # Delete the file
                    os.remove(imagepath)
                    cursor, connection = getCursor()
                    cursor.execute("""delete from image where user_id = %s and image = %s;""",
                            (member_id, option,))
                    connection.commit()

            # Display success message
            flash('Profile updated successfully', category='success')
            closeConnection()

            # Redirect to member profile page
            return redirect(url_for('member_profile'))
        
    closeConnection()
    # Render the member profile page with form and message
    return render_template('member_views.html', title='Edit Member', form=form, msg=msg)


# Route for viewing the workshop list
@app.route("/view_workshop_list", methods=['GET', 'POST'])
@logged_in
def view_workshop_list():
    # Establish database connection
    cursor, connection = getCursor()

    # Execute SQL query to retrieve workshop information
    cursor.execute("""
        SELECT 
            w.workshop_id,
            wi.workshop_info_topic,
            s.staff_id AS tutor_id,
            CONCAT(s.staff_title, ' ', s.staff_firstname, ' ', s.staff_familyname) AS tutor_name,
            w.workshop_detail,
            w.workshop_date,
            TIME_FORMAT(w.workshop_time, '%h:%i %p') AS workshop_time,
            l.location_name,
            l.location_description AS workshop_location,
            w.workshop_cost,
            l.location_map
        FROM 
            workshop w
        JOIN 
            staff s ON w.workshop_tutor_id = s.staff_id
        JOIN 
            workshop_info wi ON w.workshop_title_id = wi.workshop_info_id
        JOIN 
            location l ON w.workshop_location = l.location_id
        WHERE workshop_date > curdate()
                   order by workshop_date asc;
    """)

    workshops = cursor.fetchall()  # Fetch all workshop records

    connection.close()  # Close connection after use

    # Pass the workshops to the template along with the existing context
    return render_template("view_workshop_list.html", workshops=workshops)


# Route for viewing the details of a specific workshop
@app.route("/workshop_details/<int:workshop_id>")
@logged_in
def view_workshop_details(workshop_id):
    # Establish database connection and create cursor
    cursor, connection = getCursor()

    # Execute SQL query to retrieve details of the specified workshop
    cursor.execute("""
        SELECT 
            w.workshop_id,
            wi.workshop_info_topic,
            s.staff_id AS tutor_id,
            CONCAT(s.staff_title, ' ', s.staff_firstname, ' ', s.staff_familyname) AS tutor_name,
            w.workshop_detail,
            w.workshop_date,
            TIME_FORMAT(w.workshop_time, '%h:%i %p') AS workshop_time,
            l.location_name,
            l.location_description AS workshop_location,
            w.workshop_cost,
            l.location_map
        FROM 
            workshop w
        JOIN 
            staff s ON w.workshop_tutor_id = s.staff_id
        JOIN 
            workshop_info wi ON w.workshop_title_id = wi.workshop_info_id
        JOIN 
            location l ON w.workshop_location = l.location_id
        WHERE 
            w.workshop_id = %s;
    """, (workshop_id,))
    workshop_details = cursor.fetchone()  # Fetch the specific workshop record
    connection.close()  # Close the database connection
    
    if workshop_details:
        return render_template("view_workshop_details.html", workshop=workshop_details)
    else:
        return "Workshop not found", 404


# Route for booking a workshop
@app.route("/book_workshop/<int:workshop_id>/<int:tutor_id>", methods=['GET'])
@logged_in
def book_workshop(workshop_id, tutor_id):
    # Check if the member subscription is still active
    member_id = session['id']
    cursor, connection = getCursor()

    # Execute the SQL query to check member subscription
    cursor.execute("SELECT * FROM member WHERE member_subscription_expiry_date < CURDATE() and  member_id = %s", (member_id,))
    member = cursor.fetchone()

    # If subscription has expired, show a message and redirect to workshop list
    if member:
        flash(f'Your subscription has expired. Please renew before you make a booking', category='danger')
        return redirect(url_for('view_workshop_list'))
    else:
        # Show the details of the workshop one-on-one session
        return render_template("book_workshop.html", workshop_id=workshop_id)
    

# Route for handling workshop booking and payment
@app.route('/bookingpayment_workshop/<int:workshop_id>', methods=['GET', 'POST'])
@logged_in
def bookingpayment_workshop(workshop_id):
    # Establish database connection and create cursor
    cursor, connection = getCursor()

    # Fetch the workshop cost from the database
    cursor.execute("""
        SELECT workshop_cost
        FROM workshop
        WHERE workshop_id = %s;
    """, (workshop_id,))
    workshop_cost = cursor.fetchone()[0]  # Fetch the workshop cost
    connection.close()

    if request.method == 'POST':
        # Obtain info from form
        member_id = session['id']
        payment_amount_with_symbol = request.form.get('amountDue')
        payment_amount = float(payment_amount_with_symbol.replace('$', ''))

        # Connect to MySQL database
        cursor, connection = getCursor()

        #check if the member has already booked for the same workshop before
        cursor.execute("SELECT * FROM booking WHERE booking_workshop_id = %s and booking_member_id = %s", (workshop_id, member_id,))
        booked = cursor.fetchone()

        # If the member has already booked the workshop, display a message and redirect
        if booked is not None:
            flash(f'You have already booked this workshop. Please confirm the workshop that you would like to book', category='danger')
            return render_template("bookingpayment_workshop.html", workshop_id=workshop_id, workshop_cost=workshop_cost)

        # Calculate payment date
        payment_date = datetime.now().strftime('%Y-%m-%d')

        # Insert data into payment table
        sql_payment = """INSERT INTO payment (payment_type, payment_workshop_id, 
        payment_lesson_id, payment_subscription_id, payment_date, payment_payor_id, payment_amount) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        parameters_payment = ('C', workshop_id, None, None, payment_date, member_id, payment_amount)
        cursor.execute(sql_payment, parameters_payment)

  
        # Fetch tutor ID associated with the workshop
        cursor.execute("SELECT workshop_tutor_id FROM workshop WHERE workshop_id = %s", (workshop_id,))
        tutor = cursor.fetchone()

        # Insert data into booking table
        sql_booking = """INSERT INTO booking (booking_member_id, booking_workshop_id, 
        booking_staff_id, booking_date) 
        VALUES (%s, %s, %s, %s)"""
        parameters_booking = (member_id, workshop_id, tutor[0], payment_date)
        cursor.execute(sql_booking, parameters_booking)

        connection.commit()
        connection.close()

        return render_template('booking_payment_success.html', payment_amount=payment_amount)
    else:
        return render_template("bookingpayment_workshop.html", workshop_id=workshop_id, workshop_cost=workshop_cost)


# Route for displaying booked workshops
@app.route('/show_booked_workshop', methods=['GET', 'POST'])
@logged_in
def show_booked_workshop():
    # Get the member's ID from the session
    member_id = session.get('id')

    # Connect to the database
    cursor, connection = getCursor()
    # Execute SQL query to retrieve booked workshops for the member
    cursor.execute( """
        SELECT  
            booking_member_id AS member_id,
            w.workshop_id, 
            wi.workshop_info_topic, 
            w.workshop_detail AS workshop_description,
            w.workshop_date, 
             TIME_FORMAT(w.workshop_time, '%h:%i %p') AS workshop_time,
            l.location_name AS workshop_location, 
            l.location_description,
            w.workshop_cost,
            b.booking_id,
            l.location_map
        FROM booking b
        JOIN workshop w ON b.booking_workshop_id = w.workshop_id
        JOIN workshop_info wi ON w.workshop_title_id = wi.workshop_info_id
        JOIN location l ON w.workshop_location = l.location_id
        where w.workshop_date > curdate() and b.booking_member_id = %s
        order by w.workshop_date asc;""", (member_id,))

    # Execute the query with member_id as parameter
    booked_workshop = cursor.fetchall()  # Fetch all workshop records

    connection.close()

    # Pass the booked workshops data to the template
    return render_template('show_booked_workshop.html', booking_member_id=member_id, booked_workshop=booked_workshop)


# Route for cancelling a workshop booking
@app.route('/cancel_workshop_booking/', methods=['POST'])
@logged_in
def cancel_workshop_booking():
    # Get the booking ID from the request form data
    booking_id = request.form.get('booking_id')

    # Check if the booking_id is provided
    if not booking_id:
        flash("Booking ID is required", "error")
        return redirect(url_for('show_booked_workshop'))

    # Connect to the database
    cursor, connection = getCursor()

    try:
        
        # Fetch workshop_id and memberid associated with the booking
        cursor.execute("SELECT booking_workshop_id, booking_member_id FROM booking WHERE booking_id = %s", (booking_id,))
        booking = cursor.fetchone()

        payment_workshop_id = booking[0]
        payment_payor_id = booking[1]

        cursor.execute("SELECT payment_amount FROM payment WHERE payment_payor_id = %s and payment_workshop_id = %s", (payment_payor_id, payment_workshop_id,))
        payment = cursor.fetchone()

        payment_amount = payment[0]

        # Execute SQL query to delete the paymnet
        cursor.execute("DELETE FROM payment WHERE payment_payor_id = %s and payment_workshop_id = %s", (payment_payor_id, payment_workshop_id,))
        connection.commit()
        
        # Execute SQL query to delete the booking
        cursor.execute("DELETE FROM booking WHERE booking_id = %s", (booking_id,))
        connection.commit()

        # Close cursor and connection
        cursor.close()
        connection.close()

        return render_template('payment_refund.html', payment_amount=payment_amount, view="workshop")

    except Exception as e:
        # Rollback changes if an error occurs
        connection.rollback()
        # Display error message
        flash("An error occurred: " + str(e), "error")
        return redirect(url_for('show_booked_workshop'))


# Route for viewing the list of tutors
@app.route("/view_tutor_list", methods=['GET', 'POST'])
@logged_in
def view_tutor_list():
    cursor, connection = getCursor()
    # Execute SQL query to fetch tutor list
    cursor.execute("""
        SELECT 
        u.user_id, 
        u.username, 
        s.staff_title, 
        s.staff_firstname, 
        s.staff_familyname, 
        s.staff_position, 
        s.staff_phonenumber, 
        s.staff_email, 
        s.staff_profile, 
        i.image
        FROM user u
        JOIN staff s ON u.user_id = s.staff_id and u.userrole='TT'
        LEFT JOIN image i ON u.user_id = i.user_id  ;
    """)
    
    tutor_list = cursor.fetchall()  # Fetch all workshop records

    connection.close()  # Close connection after use
    # Pass the workshops to the template along with the existing context
    return render_template("view_tutor_list.html", tutor_list=tutor_list)


# Route for viewing the details of a specific tutor
@app.route("/view_tutor_details/<int:user_id>", methods=['GET'])
@logged_in
def view_tutor_details(user_id):
    cursor, connection = getCursor()
    # Execute SQL query to fetch tutor details
    cursor.execute("""
        SELECT 
            u.user_id,
            u.username,
            s.staff_title,
            s.staff_firstname,
            s.staff_familyname,
            s.staff_position,
            s.staff_phonenumber,
            s.staff_email,
            s.staff_profile,
            i.image,
            l.lesson_id,
            li.lesson_info_type,
            li.lesson_info_desc
        FROM 
            user u
        JOIN 
            staff s ON u.user_id = s.staff_id
        LEFT JOIN 
            image i ON u.user_id = i.user_id
        LEFT JOIN 
            lesson l ON s.staff_id = l.lesson_tutor_id
        LEFT JOIN 
            lesson_info li ON l.lesson_title_id = li.lesson_info_id
        WHERE l.lesson_booked = false and u.user_id = %s
    """, (user_id,))

    # Fetch tutor information
    tutor_details = cursor.fetchone()  # Fetch tutor information
    connection.close()  # Close connection after use

    if tutor_details:
        return render_template("view_tutor_details.html", tutor=tutor_details)
    else:
        # Redirect to the tutor list page if tutor not found
        return redirect(url_for('view_tutor_list'))


# Route for viewing the lessons of a specific tutor
@app.route("/view_tutor_lessons/<int:user_id>", methods=['GET'])
@logged_in
def view_tutor_lessons(user_id):
    cursor, connection = getCursor()

    # Execute SQL query to fetch tutor's lessons
    cursor.execute("""
    SELECT 
        l.lesson_id,
        li.lesson_info_type,
        l.lesson_detail,
        loc.location_name,
        loc.location_description,
        loc.location_map,
        loc.location_limit,
        l.lesson_date,
        TIME_FORMAT(l.lesson_start_time, '%h:%i %p') AS formatted_start_time,
        l.lesson_tutor_id 
    FROM 
        lesson l
    JOIN 
        lesson_info li ON l.lesson_title_id = li.lesson_info_id
    JOIN 
        location loc ON l.lesson_location = loc.location_id
    WHERE 
        l.lesson_booked = false and l.lesson_tutor_id = %s
""", (user_id,))

    # Fetch tutor's lessons
    tutor_lessons = cursor.fetchall()  
    connection.close()  # Close connection after use

    if tutor_lessons:
        return render_template("view_tutor_lessons.html", lessons=tutor_lessons)
    else:
        # Redirect to some page indicating no lessons found
        return redirect(url_for('view_tutor_list'))

    
    
# Route for viewing details of a one-on-one lesson with a tutor
@app.route("/view_tutor_one_on_one/<int:lesson_id>/<int:tutor_id>", methods=['GET'])
@logged_in
def view_tutor_one_on_one(lesson_id, tutor_id):
    #check if the member subscription is still active
    member_id = session['id']
    cursor, connection = getCursor()

    # Fetch the cost of the lesson subscription
    cursor.execute("select subscription_cost from subscription where subscription_type = 'L'")
    lesson_cost = cursor.fetchone()

    # Execute the SQL query to get the member_id using GID
    cursor.execute("SELECT * FROM member WHERE member_subscription_expiry_date < CURDATE() and  member_id = %s", (member_id,))
    member = cursor.fetchone()
    if member:
        # Flash message and redirect if subscription has expired
        flash(f'Your subscription has expired. Please renew before you make a booking', category='danger')
        return redirect(url_for('view_tutor_lessons', user_id=tutor_id))
    else:
        # Render the template for viewing one-on-one lesson details
        return render_template("view_tutor_one_on_one.html", lesson_id=lesson_id, lesson_cost = lesson_cost)


# payment for lesson booking
@app.route('/bookingpayment/<int:lesson_id>', methods=['GET', 'POST'])
def bookingpayment(lesson_id):
    if request.method == 'POST':
        # obtain info from form
        member_id = session['id']
        payment_amount_with_symbol = request.form.get('amountDue')

        # Remove non-numeric characters and convert to float
        payment_amount = float(re.sub(r'[^\d.]', '', payment_amount_with_symbol))

        # Connect to MySQL database      
        cursor, connection = getCursor()

        # calculate payment date
        payment_date = datetime.now().strftime('%Y-%m-%d')
        
        # insert data into payment table
        sql_payment = """INSERT INTO payment (payment_type, payment_workshop_id, 
        payment_lesson_id, payment_subscription_id, payment_date, payment_payor_id, payment_amount) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        parameters_payment = ('C', None, lesson_id, None, payment_date, member_id, payment_amount)
        cursor.execute(sql_payment, parameters_payment)

        # Set the lesson status to booked
        cursor.execute("""Update lesson set lesson_booked=True where lesson_id = %s""",( lesson_id,))

        # Fetch tutor ID associated with the lesson
        cursor.execute("SELECT lesson_tutor_id FROM lesson WHERE lesson_id = %s", (lesson_id,))
        tutor = cursor.fetchone()

        # insert data into booking table
        sql_booking = """INSERT INTO booking (booking_member_id, booking_lesson_id, 
        booking_staff_id, booking_date) 
        VALUES (%s, %s, %s, %s)"""
        parameters_booking = (member_id, lesson_id, tutor[0], payment_date)
        cursor.execute(sql_booking, parameters_booking)

        connection.commit()
        connection.close()

        return render_template('booking_payment_success.html', payment_amount=payment_amount)
    else:
        return render_template('view_tutor_one_on_one.html',lesson_id=lesson_id)


# Route for displaying booked lessons for a member
@app.route('/show_booked_lesson', methods=['GET', 'POST'])
@logged_in
def show_booked_lesson():
    # Get the member ID from the session
    member_id = session.get('id')

    # Connect to the database
    cursor, connection = getCursor()
    # Execute SQL query to fetch booked lessons for the member
    cursor.execute("""
        SELECT  
            booking_member_id AS member_id,
            l.lesson_id, 
            li.lesson_info_type, 
            l.lesson_detail AS lesson_description,
            l.lesson_date, 
             TIME_FORMAT(l.lesson_start_time, '%h:%i %p') AS lesson_start_time,
            loc.location_name AS lesson_location, 
            loc.location_description,
            l.lesson_booked,
            b.booking_id
        FROM booking b
        JOIN lesson l ON b.booking_lesson_id = l.lesson_id
        JOIN lesson_info li ON l.lesson_title_id = li.lesson_info_id
        JOIN location loc ON l.lesson_location = loc.location_id
        WHERE l.lesson_date > curdate() and b.booking_member_id = %s
        ORDER BY l.lesson_date asc ;
    """, (member_id,))

    # Execute the query with member_id as parameter
    booked_lessons = cursor.fetchall()  # Fetch all lesson records

    connection.close()

    # Pass the booked lessons data to the template
    return render_template('show_booked_lesson.html', booking_member_id=member_id, booked_lessons=booked_lessons)


# Route for canceling a lesson booking
@app.route('/cancel_lesson_booking', methods=['POST'])
@logged_in
def cancel_lesson_booking():
    # Get the booking ID from the request form data
    booking_id = request.form.get('booking_id')

    # Check if the booking_id is provided
    if not booking_id:
        # Flash an error message if booking ID is not provided
        flash("Booking ID is required", "error")
        # Redirect to the page showing booked lessons
        return redirect(url_for('show_booked_lesson'))

    # Connect to the database
    cursor, connection = getCursor()

    try:
        
        cursor.execute("SELECT booking_lesson_id, booking_member_id FROM booking WHERE booking_id = %s", (booking_id,))
        booking = cursor.fetchone()

        payment_lesson_id = booking[0]
        payment_payor_id = booking[1]

        cursor.execute("SELECT payment_amount FROM payment WHERE payment_payor_id = %s and payment_lesson_id = %s", (payment_payor_id, payment_lesson_id,))
        payment = cursor.fetchone()

        payment_amount = payment[0]

        # Execute SQL query to delete the paymnet
        cursor.execute("DELETE FROM payment WHERE payment_payor_id = %s and payment_lesson_id = %s", (payment_payor_id, payment_lesson_id,))
        connection.commit()
        
        # Execute SQL query to delete the booking
        cursor.execute("DELETE FROM booking WHERE booking_id = %s", (booking_id,))
        connection.commit()

        # Close cursor and connection
        cursor.close()
        connection.close()

        return render_template('payment_refund.html', payment_amount=payment_amount, view="lesson")

    except Exception as e:
        # Rollback changes if an error occurs
        connection.rollback()
        # Flash an error message with the details of the error
        flash("An error occurred: " + str(e), "error")
        return redirect(url_for('show_booked_lesson'))


# Route for managing member subscriptions
@app.route('/manage_subscriptions', methods=['GET', 'POST'])
@logged_in
def member_subscription():
    # Get the member ID from the session
    member_id = session['id']
    msg = ''
    form = MemberSubscriptionForm()             # Initialize the subscription form
    current_date = datetime.now().date()        # Get the current date
    member_data = None
    payment_data = None
    subscription_data = None
    
    cursor, connection = getCursor()

    # Fetch subscription data for both monthly and yearly subscriptions
    cursor.execute("""
        SELECT subscription_type, subscription_cost, subscription_discount
        FROM subscription
        WHERE subscription_type IN ('M', 'Y')
    """)
    subscription_results = cursor.fetchall()

    # Extract subscription data into a dictionary
    subscription_dict = {result[0]: {'cost': int(result[1]), 'discount': int(result[2])} for result in subscription_results}
    monthly_fee = subscription_dict.get('M', {}).get('cost')
    yearly_fee = subscription_dict.get('Y', {}).get('cost')
    monthly_discount = subscription_dict.get('M', {}).get('discount')
    yearly_discount = subscription_dict.get('Y', {}).get('discount')

    if request.method == 'GET':
        # Fetch member data
        cursor.execute('''
            SELECT NULL, member_subscription_type, member_subscription_expiry_date
            FROM member
            WHERE member_id = %s
        ''', (member_id,))
        member_data = cursor.fetchone()

        # Fetch payment data
        cursor.execute('''
            SELECT payment_subscription_id, payment_date, payment_amount
            FROM payment
            WHERE payment_payor_id = %s
            AND payment_subscription_id IN (1, 2)
            ''', (member_id,))
        payment_data = cursor.fetchall()

        # Fetch subscription data based on subscription ID associated with the user
        cursor.execute('''
            SELECT s.subscription_type, s.subscription_cost, s.subscription_discount
            FROM subscription s
            INNER JOIN member m ON s.subscription_type = m.member_subscription_type
            WHERE m.member_id = %s;
        ''', (member_id,))
        subscription_data = cursor.fetchone()

        # Extract subscription_discount from subscription_data
        subscription_discount = subscription_data[2] if subscription_data else None

        if member_data:
            form.subscription.data = member_data[1] # Populate subscription form with member's current subscription
            form.expirydate.data = member_data[2] # Populate expiry date in the form
            expiry_date = member_data[2]  # Update expiry_date here

    elif request.method == 'POST':
         # Fetch member data
        cursor.execute('''
            SELECT NULL, member_subscription_type, member_subscription_expiry_date
            FROM member
            WHERE member_id = %s
        ''', (member_id,))
        member_data = cursor.fetchone()

        # Fetch payment data
        cursor.execute('''
            SELECT payment_subscription_id, payment_date, payment_amount
            FROM payment
            WHERE payment_payor_id = %s
            AND payment_subscription_id IN (1, 2)
            ''', (member_id,))
        payment_data = cursor.fetchall()

        # Get subscription type and renewal period from the form
        subscription_type = request.form.get('subscription')
        renew_months = int(request.form.get('renewMonths')) if request.form.get('renewMonths') else 0
        renew_years = int(request.form.get('renewYears')) if request.form.get('renewYears') else 0

        expiry_date = member_data[2]    # Get current expiry date

        if subscription_type in ('M', 'Y'):
            payment_subscription_id = 1 if subscription_type == 'M' else 2
            renew_duration = renew_months * 30 if subscription_type == 'M' else renew_years * 365

            # Calculate new expiry date based on renewal period
            expiry_date = expiry_date + timedelta(days=renew_duration) if expiry_date else datetime.now().date() + timedelta(days=renew_duration)
        else:
            return "Invalid subscription type"

        # Get the amount due for payment
        amount_due = request.form.get('amountDue')

        # Insert payment record into the database
        cursor.execute('''
            INSERT INTO payment (payment_payor_id, payment_type, payment_subscription_id, payment_date, payment_amount)
            VALUES (%s, %s, %s, %s, %s)
        ''', (member_id, 'C', payment_subscription_id, datetime.now(), amount_due))

        # Update member's subscription details in the database
        cursor.execute('''
            UPDATE member
            SET member_subscription_expiry_date = %s,
                member_subscription_type = %s
            WHERE member_id = %s
        ''', (expiry_date, subscription_type, member_id))

        connection.commit()

        cursor.close()
        connection.close()
        return render_template('subscription_renew_success.html', payment_amount=amount_due)

    return render_template('member_subscription.html', monthly_fee=monthly_fee, yearly_fee=yearly_fee,
                           monthly_discount=monthly_discount, yearly_discount=yearly_discount,
                           subscription_discount=subscription_discount, subscription_data=subscription_data,
                           current_date=current_date, member_data=member_data, payment_data=payment_data,
                           form=form, msg=msg)
