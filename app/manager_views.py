from app import app
from flask import render_template, session, redirect, url_for, request, flash
import mysql.connector
import app.connect as connect
from app.utility import logged_in

from app.forms import AddMemberForm, EditMemberForm, AddTutorForm, EditTutorForm, AddWorkshopTypeForm, AddaLessonForm, EditaLessonForm

from app.forms import EditWorkshopTypeForm, EditTutorProfileForm, editPricesForm, AddLessonTypeForm, EditLessonTypeForm
from app.forms import EditLocationForm, NewsForm, EditNewsForm,  AddLocationForm, EditMemberProfileForm
import re, calendar
from werkzeug.utils import secure_filename
import os, uuid  # For generating unique identifiers
from flask import jsonify

from datetime import date, timedelta, time, datetime


# Create an instance of hashing
from flask_hashing import Hashing
hashing = Hashing(app)

# Function to establish database connection and return cursor
def getCursor():
    global dbconn
    global connection
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

def closeConnection():
    global dbconn
    global connection
    if dbconn:
        dbconn.close()
    if connection:
        connection.close()

@app.route('/manager_home')
@logged_in
def manager_home():

    user_id = session['id']
    image = None
    # Establish database connection
    cursor, connection = getCursor()

    # Fetch image associated with the logged-in user
    cursor.execute('SELECT * FROM image WHERE user_id = %s', (session['id'],) )
    image_data = cursor.fetchone()

    if image_data:
        image = image_data[2]

    cursor.execute("""SELECT CONCAT(staff_title, ' ', staff_firstname, ' ', staff_familyname) 
                    AS userfullname FROM staff WHERE staff_id = %s""", (session['id'],))
    userfullname = cursor.fetchone()[0]

    # Close database connection
    closeConnection()

    # Pass image data to the template
    return render_template('manager_home.html', user_id=user_id, image=image, userfullname=userfullname)

# Profile route
@app.route('/manager/profile', methods=['GET', 'POST'])
@logged_in
def manager_profile():

    tutorid = session['id']
    # Fetch the user's profile information from the database
    msg=''
    form=EditTutorProfileForm()

    if request.method == 'GET':
        cursor, connection = getCursor()
        cursor.execute('SELECT * FROM staff WHERE staff_id = %s', (tutorid,) )
        profileList = cursor.fetchall()
        form.title.data = profileList[0][1]
        form.firstname.data = profileList[0][2]
        form.lastname.data = profileList[0][3]
        tutorname = profileList[0][2] + ' ' + profileList[0][3]
        form.position.data = profileList[0][4]
        form.phone.data = profileList[0][5]
        form.email.data = profileList[0][6]
        form.profile.data = profileList[0][7]

        #retrieve the user status and role from user table
        cursor, connection = getCursor()
        cursor.execute('select * from user where user_id = %s', (tutorid,))
        userprofile = cursor.fetchall()

        #retrieve tutor image from image table
        cursor, connection = getCursor()
        cursor.execute('select * from image where user_id = %s', (tutorid,))
        imagelist = cursor.fetchall()
        form.images.choices =  [(image[2]) for image in imagelist]

        closeConnection()
        return render_template("manager_views.html", form=form, tutor_id = tutorid, tutorname = tutorname)

  
    elif request.method == 'POST':
       if form.validate_on_submit():

        tutor_id = request.form.get('tutor_id')
        title = form.title.data
        firstname = form.firstname.data
        lastname = form.lastname.data
        position = form.position.data
        phone = form.phone.data
        email = form.email.data
        profile = form.profile.data

        cursor, connection = getCursor()
        cursor.execute("""UPDATE staff SET staff_title=%s, staff_firstname=%s, staff_familyname= %s, 
                       staff_position =%s, staff_phonenumber =%s, staff_email =%s, staff_profile =%s
                    WHERE staff_id = %s;""",
                            ( title, firstname, lastname, position, phone, email, profile, tutor_id,))

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
                    (tutor_id, new_filename,))
        
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
                        (tutor_id, option,))
                connection.commit()

        flash('Profile updated successfully', category='success')
        closeConnection()
        return redirect(url_for('manager_profile'))
    closeConnection()
    return render_template('manager_views.html', title='Edit Manager', form=form, msg=msg)

@app.route("/viewmemberlist", methods=['GET'])
@logged_in
def viewmemberlist():
    #function will return all the members
    cursor, connection = getCursor()
    cursor.execute("select * from user a, member b where a.user_id = b.member_id")
    memberlist = cursor.fetchall()
    closeConnection()
    return render_template("member_list.html", member_list = memberlist)

@app.route("/manage_prices", methods=['GET'])
@logged_in
def manage_prices():
    #function will return all the prices 
    form=editPricesForm()

    cursor, connection = getCursor()
    cursor.execute("""SELECT
            (SELECT subscription_cost FROM subscription WHERE subscription_type = 'M') AS MonthlySubFee,
            (SELECT subscription_discount FROM subscription WHERE subscription_type = 'M') AS MonthlySubDiscount,
            (SELECT subscription_cost FROM subscription WHERE subscription_type = 'Y') AS AnnualSubFee,
            (SELECT subscription_discount FROM subscription WHERE subscription_type = 'Y') AS AnnualSubDiscount,
            (SELECT subscription_cost FROM subscription WHERE subscription_type = 'L') AS LessonFee;""")
    result = cursor.fetchone()

    #we have to convert the prices to float before displaying them in the fields 
    form.annualsubfee.data = float(result[2])
    form.monthlysubfee.data = float(result[0])
    form.lessonfee.data = float(result[4])
    form.annualsubdiscount.data = float(result[3])
    form.monthlysubdiscount.data = float(result[1])

    connection.close()
    return render_template("manage_prices.html", form=form)

@app.route("/manage_workshop_prices", methods=['GET'])
@logged_in
def manage_workshop_prices():
    #retrieve all the available workshops so that the manager can edit the workshops prices
    #this list is to be sorted by ascending workshop date 
    cursor, connection = getCursor()
    cursor.execute( """
            SELECT 
                w.workshop_id AS workshop_id,
                CONCAT(s.staff_title, ' ', s.staff_firstname, ' ', s.staff_familyname) AS tutor,
                wi.workshop_info_topic,
                wi.workshop_info_desc AS workshop_detail,
                w.workshop_date AS workshop_date,
                TIME_FORMAT(w.workshop_time, '%h:%i %p') AS workshop_time,
                CONCAT(l.location_name, ' ', l.location_description) AS workshop_location,
                w.workshop_cost AS workshop_cost,
                w.workshop_cap_limit AS workshop_cap_limit,
                w.workshop_attendance AS workshop_attendance
            FROM 
                workshop w
            INNER JOIN 
                staff s ON w.workshop_tutor_id = s.staff_id
            INNER JOIN 
                workshop_info wi ON w.workshop_title_id = wi.workshop_info_id
            INNER JOIN 
                location l ON w.workshop_location = l.location_id
            ORDER BY workshop_date ASC;
                """)
    workshop_list = cursor.fetchall()
    number_of_records = cursor.rowcount
    connection.close()
    return render_template("manage_workshop_prices.html", workshoplist=workshop_list, number_of_records=number_of_records)

@app.route("/updateprices", methods=['POST'])
@logged_in
def updateprices():
    #function will update all the subscription and lesson fee prices
    form=editPricesForm()

    monthlysubfee = form.monthlysubfee.data
    monthlysubdiscount = form.monthlysubdiscount.data
    annualsubfee = form.annualsubfee.data
    annualsubdiscount = form.annualsubdiscount.data
    lessonfee = form.lessonfee.data 

    cursor, connection = getCursor()
    cursor.execute("""Update subscription set subscription_cost = %s where subscription_type = 'M';""", (monthlysubfee,))
    cursor.execute("""Update subscription set subscription_cost = %s where subscription_type = 'Y';""", (annualsubfee,))
    cursor.execute("""Update subscription set subscription_discount = %s where subscription_type = 'M';""", (monthlysubdiscount,))
    cursor.execute("""Update subscription set subscription_discount = %s where subscription_type = 'Y';""", (annualsubdiscount,))
    cursor.execute("""Update subscription set subscription_cost = %s where subscription_type = 'L';""", (lessonfee,))
    connection.commit()
    connection.close()

    flash(f'Prices updated successfully', category='success')
    return render_template("manage_prices.html", form=form)

@app.route("/updateworkshopprices", methods=['POST'])
@logged_in
def updateworkshopprices():
    #function will update all the workshop prices 
    #the for loop will loop throught the entire form to get the workshop_id and the workshop price
    #update statement will be triggered within each of the loop
    cursor, connection = getCursor()
    for key, value in request.form.items():
        if key.startswith('workshop_cost_'):
            workshop_id = key.split('_')[2]  # Extract the workshop ID from the key
            workshop_cost = value 
            cursor.execute("""UPDATE workshop SET workshop_cost = %s WHERE workshop_id = %s;""", (workshop_cost, workshop_id,))
            connection.commit()

    #once all the workshop prices are updated
    #the list will be retrieved and the page will be repopulated
    cursor.execute( """
        SELECT 
            w.workshop_id AS workshop_id,
            CONCAT(s.staff_title, ' ', s.staff_firstname, ' ', s.staff_familyname) AS tutor,
            wi.workshop_info_topic,
            wi.workshop_info_desc AS workshop_detail,
            w.workshop_date AS workshop_date,
            TIME_FORMAT(w.workshop_time, '%h:%i %p') AS workshop_time,
            CONCAT(l.location_name, ' ', l.location_description) AS workshop_location,
            w.workshop_cost AS workshop_cost,
            w.workshop_cap_limit AS workshop_cap_limit,
            w.workshop_attendance AS workshop_attendance
        FROM 
            workshop w
        INNER JOIN 
            staff s ON w.workshop_tutor_id = s.staff_id
        INNER JOIN 
            workshop_info wi ON w.workshop_title_id = wi.workshop_info_id
        INNER JOIN 
            location l ON w.workshop_location = l.location_id
        ORDER BY workshop_date ASC;
            """)
    workshop_list = cursor.fetchall()
    number_of_records = cursor.rowcount
    connection.close()

    flash(f'Prices updated successfully', category='success')
    return render_template("manage_workshop_prices.html", workshoplist=workshop_list, number_of_records=number_of_records)

@app.route('/deletemember', methods=['POST'])
@logged_in
def deletemember():
    #function to delete member
    #member ID retrieved from caller form
    #caller: memberlist.html
    cursor, connection = getCursor()

    member_id = int(request.form.get('memberID'))

    #as there are foreign key of member_id in the payment table, we couldn't just delete the member from the member table
    #we have to first delete the payment information of this member
    #we will also have to delete this member from the user table
    cursor.execute("""delete from payment where payment_payor_id = %s;""",
            (member_id,))

    cursor.execute("""delete from member where member_id = %s;""",
            (member_id,))

    cursor, connection = getCursor()
    cursor.execute("""delete from user where user_id = %s;""",
            (member_id,))
    
    connection.commit()
    
    flash(f'Member deleted successfully', category='success')

    closeConnection()
    return redirect("/viewmemberlist")

@app.route("/viewtutorlist", methods=['GET'])
@logged_in
def viewtutorlist():
    #function will return all the tutors
    #tutor user role is TT
    cursor, connection = getCursor()
    cursor.execute("""SELECT * FROM user a JOIN staff b ON a.user_id = b.staff_id 
                   LEFT OUTER JOIN image c ON a.user_id = c.user_id WHERE a.userrole = 'TT';""")
    tutorlist = cursor.fetchall()

    closeConnection()

    return render_template("tutor_list.html", tutor_list = tutorlist)

@app.route("/viewlocationlist", methods=['GET'])
@logged_in
def viewlocationlist():
    #function will return all the locations
    cursor, connection = getCursor()
    cursor.execute("""SELECT * FROM location;""")
    locationlist = cursor.fetchall()

    connection.close()

    return render_template("location_list.html", location_list = locationlist)

@app.route('/addlocation')
@logged_in
def addlocation():
    form = AddLocationForm()
    return render_template('add_location.html', form=form)

@app.route("/viewworkshoptypelist", methods=['GET'])
@logged_in
def viewworkshoptypelist():

    #function will return all the workshop type
    cursor, connection = getCursor()
    cursor.execute("select * from workshop_info;")
    workshoptypelist = cursor.fetchall()

    closeConnection()

    return render_template("workshop_type_list.html", workshoptype_list = workshoptypelist)

@app.route("/viewlessontypelist", methods=['GET'])
@logged_in
def viewlessontypelist():
    #function will return all the lesson type
    cursor, connection = getCursor()
    cursor.execute("select * from lesson_info;")
    lessontypelist = cursor.fetchall()

    closeConnection()

    return render_template("lesson_type_list.html", lessontype_list = lessontypelist)

@app.route('/deletelessontype', methods=['POST'])
@logged_in
def deletelessontype():
    #function to delete lesson type
    #lessontype ID retrieved from caller form
    #caller: lesson_type_list.html
    cursor, connection = getCursor()

    lessontype_id = int(request.form.get('lessontypeID'))

    cursor.execute("""delete from lesson_info where lesson_info_id = %s;""",
            (lessontype_id,))
    
    connection.commit()
    closeConnection()
    
    flash(f'Lesson Type deleted successfully', category='success')

    closeConnection()
    return redirect("/viewlessontypelist")

@app.route('/deleteworkshoptype', methods=['POST'])
@logged_in
def deleteworkshoptype():
    #function to delete workshoptype
    #workshoptype ID retrieved from caller form
    #caller: workshop_type_list.html
    cursor, connection = getCursor()

    workshoptype_id = int(request.form.get('workshoptypeID'))

    cursor.execute("""delete from workshop_info where workshop_info_id = %s;""",
            (workshoptype_id,))
    
    connection.commit()
    closeConnection()
    
    flash(f'Workshop Type deleted successfully', category='success')

    closeConnection()
    return redirect("/viewworkshoptypelist")

@app.route('/deletetutor', methods=['POST'])
@logged_in
def deletetutor():
    #function to delete tutor
    #tutor ID retrieved from caller form
    #caller: tutor_list.html
    tutor_id = int(request.form.get('tutorID'))
    
    cursor, connection = getCursor()
    cursor.execute("""delete from staff where staff_id = %s;""",
            (tutor_id,))
    
    connection.commit()
    closeConnection()
    #2nd to get all the images
    cursor, connection = getCursor()
    cursor.execute('select * from image where user_id = %s', (tutor_id,) )
    imagelist = cursor.fetchall()

    #logic below will delete all the physical images that belongs to this guide
    if len(imagelist) > 0:
        for image in imagelist:
            imagefilename = image[2]
            imagepath = os.path.join('app', 'static/images', imagefilename)
            # Check if the file exists before attempting to delete it
            if os.path.exists(imagepath):
            # Delete the file
                os.remove(imagepath)

    #once the physical image is delete from the server, the next step is to delete the 
    #record from the database 
    cursor, connection = getCursor()
    cursor.execute("""delete from image where user_id = %s;""",
            (tutor_id,))
    connection.commit()
    closeConnection()
    cursor, connection = getCursor()
    #we also need to delete the tutor from the user table
    cursor.execute("""delete from user where user_id = %s;""",
            (tutor_id,))
    
    connection.commit()
    
    flash(f'Tutor deleted successfully', category='success')

    closeConnection()
    return redirect("/viewtutorlist")

@app.route('/deletelocation', methods=['POST'])
@logged_in
def deletelocation():
    #function to delete location
    #location ID retrieved from caller form
    #caller: location_list.html
    location_id = int(request.form.get('locationID'))

    cursor, connection = getCursor()
    cursor.execute('select location_map from location where location_id = %s', (location_id,) )
    imagelist = cursor.fetchone()

    #logic below will delete all the physical images that belongs to this guide
    if len(imagelist) > 0:
        imagefilename = imagelist[0]
        imagepath = os.path.join('app', 'static/images',imagefilename)
        # Check if the file exists before attempting to delete it
        if os.path.exists(imagepath):
                os.remove(imagepath)
    #once the physical image is delete from the server, the next step is to delete the 
    #record from the database 
    cursor, connection = getCursor()

    cursor.execute("""delete from location where location_id = %s;""",
            (location_id,))
    
    connection.commit()
    
    flash(f'Location deleted successfully', category='success')

    closeConnection()
    return redirect("/viewlocationlist")

@app.route('/addmember')
@logged_in
def addmember():
    form = AddMemberForm()
    return render_template('add_member.html', form=form)

@app.route('/addworkshoptype')
@logged_in
def addworkshoptype():
    form = AddWorkshopTypeForm()
    return render_template('add_workshop_type.html', form=form)

@app.route('/addlessontype')
@logged_in
def addlessontype():
    form = AddLessonTypeForm()
    return render_template('add_lesson_type.html', form=form)


@app.route('/addtutor')
@logged_in
def addtutor():
    form = AddTutorForm()
    return render_template('add_tutor.html', form=form)

@app.route("/editworkshoptype/<workshoptypeid>", methods=["GET"])
@logged_in
def editworkshoptype(workshoptypeid):
    #function to retrieve workshoptype information for editing
    #workshoptype ID passed in via hyperlink
    #caller: workshop_type_list.html
    form=AddWorkshopTypeForm()
    cursor, connection = getCursor()
    cursor.execute('SELECT * FROM workshop_info where workshop_info_id = %s', (workshoptypeid,))
    profileList = cursor.fetchall()
    form.workshoptype.data = profileList[0][1]
    form.workshopdesc.data = profileList[0][2]
    workshoptypeid = profileList[0][0]
    closeConnection()
    return render_template("edit_workshop_type.html", form=form, workshoptype_id = workshoptypeid)

@app.route("/editlessontype/<lessontypeid>", methods=["GET"])
@logged_in
def editlessontype(lessontypeid):
    #function to retrieve lessontype information for editing
    #lessontype ID passed in via hyperlink
    #caller: lesson_type_list.html
    form=AddLessonTypeForm()
    cursor, connection = getCursor()
    cursor.execute('SELECT * FROM lesson_info where lesson_info_id = %s', (lessontypeid,))
    profileList = cursor.fetchall()
    form.lessontype.data = profileList[0][1]
    form.lessondesc.data = profileList[0][2]
    lessontypeid = profileList[0][0]
    closeConnection()
    return render_template("edit_lesson_type.html", form=form, lessontype_id = lessontypeid)

@app.route('/insertlessontype', methods=['POST'])
@logged_in
def insertlessontype():
    #function to create a workshoptype
    msg=''
    form=AddLessonTypeForm()
    if form.validate_on_submit():

        lessontype = form.lessontype.data
        lessondesc = form.lessondesc.data

        cursor, connection = getCursor()
        
        cursor.execute('INSERT INTO lesson_info (lesson_info_type, lesson_info_desc ) VALUES ( %s, %s)',
                        (lessontype, lessondesc, ))
        connection.commit()

        flash(f'Lesson Type created successfully', category='success')
        #once create is successful, user will be routed to the lesson type list screen
        closeConnection()
        return redirect(url_for('viewlessontypelist'))
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    closeConnection()
    return render_template('add_lesson_type.html', title='Add New Lesson Type', form=form, msg=msg)

@app.route('/insertworkshoptype', methods=['POST'])
@logged_in
def insertworkshoptype():
    #function to create a workshoptype
    msg=''
    form=AddWorkshopTypeForm()
    if form.validate_on_submit():

        workshoptype = form.workshoptype.data
        workshopdesc = form.workshopdesc.data

        cursor, connection = getCursor()
        
        cursor.execute('INSERT INTO workshop_info (workshop_info_topic, workshop_info_desc ) VALUES ( %s, %s)',
                        (workshoptype, workshopdesc, ))
        connection.commit()

        flash(f'Workshop Type created successfully', category='success')
        #once create is successful, user will be routed to the workshop type list screen
        closeConnection()
        return redirect(url_for('viewworkshoptypelist'))
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show add workshop type form with message (if any)
    closeConnection()
    return render_template('add_workshop_type.html', title='Add New Workshop Type', form=form, msg=msg)


@app.route('/updateworkshoptype', methods=['POST'])
@logged_in
def updateworkshoptype():
    #function to update workshop type
    msg=''
    form=EditWorkshopTypeForm()
    if form.validate_on_submit():

        workshoptype = form.workshoptype.data
        workshopdesc = form.workshopdesc.data
        workshoptypeID = request.form.get('workshoptype_id')

        cursor, connection = getCursor()
        
        cursor.execute('UPDATE workshop_info SET workshop_info_topic=%s, workshop_info_desc=%s WHERE workshop_info_id = %s;',
                        (workshoptype, workshopdesc, workshoptypeID))
        connection.commit()

        flash(f'Workshop Type updated successfully', category='success')
        #once registration is successful, user will be routed to the login screen
        closeConnection()
        return redirect(url_for('viewworkshoptypelist'))
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    closeConnection()
    return render_template('edit_workshop_type.html', title='Edit Workshop Type', form=form, msg=msg)

@app.route('/updatelessontype', methods=['POST'])
@logged_in
def updatelessontype():
    #function to update lesson type
    msg=''
    form=EditLessonTypeForm()
    if form.validate_on_submit():

        lessontype = form.lessontype.data
        lessondesc = form.lessondesc.data
        lessontypeID = request.form.get('lessontype_id')

        cursor, connection = getCursor()
        
        cursor.execute('UPDATE lesson_info SET lesson_info_type=%s, lesson_info_desc=%s WHERE lesson_info_id = %s;',
                        (lessontype, lessondesc, lessontypeID))
        connection.commit()

        flash(f'Lesson Type updated successfully', category='success')

        closeConnection()
        return redirect(url_for('viewlessontypelist'))
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    closeConnection()
    return render_template('edit_lesson_type.html', title='Edit Lesson Type', form=form, msg=msg)


@app.route('/insertmember', methods=['POST'])
@logged_in
def insertmember():
    #function to register/create a member
    msg=''
    form=AddMemberForm()
    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data
        email = form.email.data
        userrole = 'MM' #default role to member
 
        title = form.title.data
        firstname = form.firstname.data
        lastname = form.lastname.data
        position = form.position.data
        phone = form.phone.data
        email = form.email.data
        address = form.address.data
        dob = form.dob.data
        status = 'A' #default for Active user

        # Check if account exists using MySQL
        cursor, connection = getCursor()
        cursor.execute('SELECT * FROM user WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            hashed = hashing.hash_value(password, salt='abcd')
            cursor.execute('INSERT INTO user (username, passwordhash, userrole, status) VALUES ( %s, %s, %s, %s)',
                            (username, hashed, userrole, status, ))
            connection.commit()

            GID = cursor.lastrowid #retrieve the ID from lastrowid to be used as member_ID 

            cursor.execute('INSERT INTO member VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', 
                           (GID, title, firstname, lastname, position, phone, email, address, dob, None, None, None))
            connection.commit()

            flash(f'Account created successfully for {form.username.data}', category='success')
            #once registration is successful, user will be routed to the login screen
            closeConnection()
            return redirect(url_for('viewmemberlist'))
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    closeConnection()
    return render_template('add_member.html', title='Add New Member', form=form, msg=msg)
    
@app.route("/editmember/<memberid>", methods=["GET"])
@logged_in
def editmember(memberid):
    #function to retrieve member profile for editing
    #member ID passed in via hyperlink
    #caller: member_list.html
    form=EditMemberForm()
    cursor, connection = getCursor()
    cursor.execute('SELECT * FROM member WHERE member_id = %s', (memberid,) )
    profileList = cursor.fetchall()
    form.title.data = profileList[0][1]
    form.firstname.data = profileList[0][2]
    form.lastname.data = profileList[0][3]
    membername = profileList[0][2] + ' ' + profileList[0][3]
    form.position.data = profileList[0][4]
    form.phone.data = profileList[0][5]
    form.email.data = profileList[0][6]
    form.address.data = profileList[0][7]
    form.dob.data = profileList[0][8]

    #retrieve the user status and role from user table
    cursor, connection = getCursor()
    cursor.execute('select * from user where user_id = %s', (memberid,))
    userprofile = cursor.fetchall()

    form.status.data = userprofile[0][4] 
    closeConnection()
    return render_template("edit_member.html", form=form, member_id = memberid, membername = membername)

@app.route('/updatemember', methods=['POST'])
@logged_in
def updatemember():
    #function to update member profile
    msg=''
    member_id = None
    form=EditMemberForm() 

    if form.validate_on_submit():
        member_id = int(request.form.get('member_id'))
        title = form.title.data
        firstname = form.firstname.data
        lastname = form.lastname.data
        position = form.position.data
        phone = form.phone.data
        email = form.email.data
        address = form.address.data
        dob = form.dob.data
        status = form.status.data

        #if staff_id has value then update with values from caller
        cursor, connection = getCursor()
        cursor.execute("""UPDATE member SET member_title=%s, member_firstname=%s, member_familyname= %s, 
                       member_position =%s, member_phonenumber =%s, member_email =%s, member_dob =%s ,
                    member_address =%s
                    WHERE member_id = %s;""",
                            ( title, firstname, lastname, position, phone, email, dob, address, member_id,))
        #update user status
        cursor, connection = getCursor()
        cursor.execute("""UPDATE user SET status=%s WHERE user_id = %s;""",
                            ( status, member_id,))

        flash(f'Member {form.firstname.data} {form.lastname.data}  updated successfully', category='success')
        closeConnection()
        return redirect("/viewmemberlist")
    
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show edit member form with message (if any)
    closeConnection()
    return render_template('edit_member.html', title='Edit Member', form=form, msg=msg)

@app.route("/edittutor/<tutorid>", methods=["GET"])
@logged_in
def edittutor(tutorid):
    #function to retrieve tutor profile for editing
    #tutor ID passed in via hyperlink
    #caller: tutor_list.html
    form=EditTutorForm()
    cursor, connection = getCursor()
    cursor.execute('SELECT * FROM staff WHERE staff_id = %s', (tutorid,) )
    profileList = cursor.fetchall()
    form.title.data = profileList[0][1]
    form.firstname.data = profileList[0][2]
    form.lastname.data = profileList[0][3]
    tutorname = profileList[0][2] + ' ' + profileList[0][3]
    form.position.data = profileList[0][4]
    form.phone.data = profileList[0][5]
    form.email.data = profileList[0][6]
    form.profile.data = profileList[0][7]

    #retrieve the user status and role from user table
    cursor, connection = getCursor()
    cursor.execute('select * from user where user_id = %s', (tutorid,))
    userprofile = cursor.fetchall()

    form.status.data = userprofile[0][4] 

    #retrieve tutor image from image table
    cursor, connection = getCursor()
    cursor.execute('select * from image where user_id = %s', (tutorid,))
    imagelist = cursor.fetchall()
    form.images.choices =  [(image[2]) for image in imagelist]

    closeConnection()
    return render_template("edit_tutor.html", form=form, tutor_id = tutorid, tutorname = tutorname)

@app.route("/editlocation/<locationid>", methods=["GET"])
@logged_in
def editlocation(locationid):
    #function to retrieve location for editing
    #location ID passed in via hyperlink
    #caller: location_list.html
    form=EditLocationForm()
    cursor, connection = getCursor()
    cursor.execute('SELECT * FROM location WHERE location_id = %s', (locationid,) )
    profileList = cursor.fetchall()
    form.locationname.data = profileList[0][1]
    form.locationdesc.data = profileList[0][2]
    form.locationlimit.data = int(profileList[0][4])

    if profileList[0][3] is not None:
        form.locationmap.choices = [(profileList[0][3])]
    else:
        form.locationmap.choices = []

    closeConnection()
    return render_template("edit_location.html", form=form, location_id = locationid)

@app.route('/insertlocation', methods=['POST'])
@logged_in
def insertlocation():
    #function to create a location along with the map
    msg=''
    form=AddLocationForm()
    cursor, connection = getCursor()
    if form.validate_on_submit():

        locationname = form.locationname.data
        locationdesc = form.locationdesc.data
        limit = form.locationlimit.data
        uploaded_files = form.locationmap.data

        cursor.execute('INSERT INTO location (location_name, location_description, location_limit) VALUES ( %s, %s, %s)',
                        (locationname, locationdesc, limit, ))
        connection.commit()
        
        GID = cursor.lastrowid #retrieve the ID from lastrowid to be used as location_ID 
        # Save uploaded files to server and database
        if uploaded_files is not None:
            for idx, file in enumerate(uploaded_files):

                random_string = str(uuid.uuid4())[:8]  # Using UUID for randomness
                new_filename = random_string + '_' + file.filename
                file_path = os.path.join('app', 'static/images', new_filename)
                file.save(file_path)
                
                cursor.execute('update location Set location_map = %s where location_id = %s', 
                    (new_filename, GID,))
                connection.commit()

        flash(f'Location created successfully for {locationname}', category='success')
        #once create is successful, user will be routed to the view location list screen
        closeConnection()
        return redirect(url_for('viewlocationlist'))
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show location create form with message (if any)
    closeConnection()
    return render_template('add_location.html', title='Add New Location', form=form, msg=msg)

@app.route('/updatelocation', methods=['POST'])
@logged_in
def updatelocation():
    #function to edit location
    msg=''
    form=EditLocationForm()
    if form.validate_on_submit():

        location_id = request.form.get('location_id')
       
        locationname = form.locationname.data
        locationdesc = form.locationdesc.data
        limit = form.locationlimit.data
        uploaded_files = form.locationmap.data

        cursor, connection = getCursor()
        cursor.execute("""UPDATE location SET location_name=%s, location_description=%s, location_limit= %s 
                            WHERE location_id = %s;""",
                            ( locationname, locationdesc, limit, location_id,))
        cursor, connection = getCursor()

        # Save uploaded files to server and database
        if uploaded_files is not None:
            for idx, file in enumerate(uploaded_files):

                random_string = str(uuid.uuid4())[:8]  # Using UUID for randomness
                new_filename = random_string + '_' + file.filename
                file_path = os.path.join('app', 'static/images', new_filename)
                file.save(file_path)
                cursor, connection = getCursor()
                cursor.execute('update location Set location_map = %s where location_id = %s', 
                                    (new_filename, location_id,))
                connection.commit()
        
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
                cursor.execute('update location Set location_map = NULL where location_id = %s', 
                        (location_id,))
                connection.commit()

        flash('Location information updated successfully', category='success')
        closeConnection()
        return redirect("/viewlocationlist")
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show location form with message (if any)
    closeConnection()
    return render_template('edit_location.html', title='Edit Location', form=form, msg=msg)


@app.route('/inserttutor', methods=['POST'])
@logged_in
def inserttutor():
    #function to create a tutor
    msg=''
    form=AddTutorForm()
    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data
        email = form.email.data
        userrole = 'TT' #default role to member

        title = form.title.data
        firstname = form.firstname.data
        lastname = form.lastname.data
        position = form.position.data
        phone = form.phone.data
        email = form.email.data
        profile = form.profile.data
        status = 'A' #default for Active user
        uploaded_files = form.images.data

        # Check if account exists using MySQL
        cursor, connection = getCursor()
        cursor.execute('SELECT * FROM user WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            hashed = hashing.hash_value(password, salt='abcd')
            cursor.execute('INSERT INTO user (username, passwordhash, userrole, status) VALUES ( %s, %s, %s, %s)',
                            (username, hashed, userrole, status, ))
            connection.commit()

            GID = cursor.lastrowid #retrieve the ID from lastrowid to be used as member_ID 

            cursor.execute('INSERT INTO staff VALUES ( %s, %s, %s, %s, %s, %s, %s, %s)', 
                           (GID, title, firstname, lastname, position, phone, email, profile, ))
            connection.commit()

            # Save uploaded files to server and database
            if uploaded_files is not None:
                for idx, file in enumerate(uploaded_files):

                    random_string = str(uuid.uuid4())[:8]  # Using UUID for randomness
                    new_filename = random_string + '_' + file.filename
                    file_path = os.path.join('app', 'static/images', new_filename)
                    file.save(file_path)
                    cursor, connection = getCursor()
                    cursor.execute('INSERT INTO image ( user_id, image) VALUES (%s, %s)', 
                        (GID, new_filename,))
                    connection.commit()

            flash(f'Account created successfully for {form.username.data}', category='success')
            #once registration is successful, user will be routed to the login screen
            closeConnection()
            return redirect(url_for('viewtutorlist'))
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show add tutor form with message (if any)
    closeConnection()
    return render_template('add_tutor.html', title='Add New Tutor', form=form, msg=msg)

@app.route('/updatetutor', methods=['POST'])
@logged_in
def updatetutor():
    #function to edit tutor
    msg=''
    form=EditTutorForm()
    if form.validate_on_submit():

        tutor_id = request.form.get('tutor_id')
        title = form.title.data
        firstname = form.firstname.data
        lastname = form.lastname.data
        position = form.position.data
        phone = form.phone.data
        email = form.email.data
        profile = form.profile.data
        status = form.status.data

        cursor, connection = getCursor()
        cursor.execute("""UPDATE staff SET staff_title=%s, staff_firstname=%s, staff_familyname= %s, 
                       staff_position =%s, staff_phonenumber =%s, staff_email =%s, staff_profile =%s
                    WHERE staff_id = %s;""",
                            ( title, firstname, lastname, position, phone, email, profile, tutor_id,))
        #update user status
        cursor, connection = getCursor()
        cursor.execute("""UPDATE user SET status=%s WHERE user_id = %s;""",
                            ( status, tutor_id,))

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
                    (tutor_id, new_filename,))
        
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
                        (tutor_id, option,))
                connection.commit()

        flash('Tutor Profile updated successfully', category='success')
        closeConnection()
        return redirect("/viewtutorlist")
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show edit tutor form with message (if any)
    closeConnection()
    return render_template('edit_tutor.html', title='Edit Tutor', form=form, msg=msg)


# view subscription reports

@app.route('/subscription_report', methods=['GET', 'POST'])
@logged_in
def subscription_report():
    filter = request.form.get('filter')
    cursor, connection = getCursor()
    #if the selected filter is expired
    #return only the list of member with expired subscription
    #the list will also include those who does not have a subscription
    if filter == "expired":
        cursor.execute("""SELECT * FROM member WHERE member_subscription_expiry_date < CURDATE() ORDER BY 
                        CASE 
                            WHEN member_subscription_expiry_date IS NULL THEN 1 
                            ELSE 0 
                        END, 
                        member_subscription_expiry_date ASC""")
        expired_members = cursor.fetchall()
        return render_template('subscription_report.html', filter="expired", expired_members=expired_members)

    elif filter == "near_to_expire":
        #if the filter is near to expire
        #return the list of members where the expiry date of subscription is 3 weeks away
        cursor.execute("""SELECT * FROM member WHERE member_subscription_expiry_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 3 WEEK) 
                       ORDER BY 
                        CASE 
                            WHEN member_subscription_expiry_date IS NULL THEN 1 
                            ELSE 0 
                        END, 
                        member_subscription_expiry_date ASC""")
        near_to_expire_members = cursor.fetchall()
        return render_template('subscription_report.html', filter="near_to_expire", near_to_expire_members=near_to_expire_members)

    else:
        #lastly if there is no filter
        #return all of the members
        cursor.execute("""SELECT * FROM member ORDER BY 
                        CASE 
                            WHEN member_subscription_expiry_date IS NULL THEN 1 
                            ELSE 0 
                        END, 
                        member_subscription_expiry_date ASC""")
        members = cursor.fetchall()
        today = date.today()
        return render_template('subscription_report.html', members=members, today=today)


# view workshop reports - popularity
@app.route("/workshop_report", methods=['GET'])
@logged_in
def workshop_report():
    #retrieve all workshops order by the workshop with the most attendance
    cursor, connection =  getCursor()
    sql = """
            SELECT 
                w.workshop_id AS workshop_id,
                CONCAT(s.staff_title, ' ', s.staff_firstname, ' ', s.staff_familyname) AS tutor,
                wi.workshop_info_topic AS workshop_topic,
                wi.workshop_info_desc AS workshop_detail,
                w.workshop_date AS workshop_date,
                TIME_FORMAT(w.workshop_time, '%h:%i %p') AS workshop_time,
                CONCAT(l.location_name, ' ', COALESCE(l.location_description, '')) AS workshop_location,
                w.workshop_cost AS workshop_cost,
                w.workshop_cap_limit AS workshop_cap_limit,
                w.workshop_attendance AS workshop_attendance
            FROM 
                workshop w
            INNER JOIN 
                staff s ON w.workshop_tutor_id = s.staff_id
            INNER JOIN 
                workshop_info wi ON w.workshop_title_id = wi.workshop_info_id
            INNER JOIN 
                location l ON w.workshop_location = l.location_id
            ORDER BY workshop_attendance DESC;
                """    
    cursor.execute(sql)
    workshops = cursor.fetchall()

    #section below is data retrieved to be used in the graph
    workshop_titles = [workshop[2] for workshop in workshops]
    attendance_data = [workshop[9] for workshop in workshops]
    time_formatted = [workshop[5] for workshop in workshops]
    workshop_details = [f"Date: {workshop[4].strftime('%d-%m-%Y')}, Time: {time}, Tutor: {workshop[1]}" for workshop, time in zip(workshops, time_formatted)]

    return render_template('workshop_report.html', workshops=workshops, workshop_titles=workshop_titles, attendance_data=attendance_data, workshop_details=workshop_details)


# view patterns report
@app.route("/patterns_report", methods=['GET', 'POST'])
@logged_in
def patterns_report():
    cursor, connection =  getCursor()

    filter = request.form.get('filter')
    show = ""
    dateFrom = ""
    dateTo = ""

    if request.method == 'POST':
        show = request.form.get('show')
        dateFrom = request.form.get('start')
        dateTo = request.form.get('end')

    #check if the date from and date to is entered 
    #if the user clicked on Show, then the sql needs to filter the dates
    #below workshop and lesson sections retrieved information to be used in the graph
    if show =="show":

        sql = """
        SELECT 
            w.workshop_id AS workshop_id,
            CONCAT(s.staff_title, ' ', s.staff_firstname, ' ', s.staff_familyname) AS tutor,
            wi.workshop_info_topic AS workshop_topic,
            wi.workshop_info_desc AS workshop_detail,
            w.workshop_date AS workshop_date,
            TIME_FORMAT(w.workshop_time, '%h:%i %p') AS workshop_time,
            CONCAT(l.location_name, ' ', l.location_description) AS workshop_location,
            w.workshop_attendance AS workshop_attendance
        FROM 
            workshop w
        INNER JOIN 
            staff s ON w.workshop_tutor_id = s.staff_id
        INNER JOIN 
            workshop_info wi ON w.workshop_title_id = wi.workshop_info_id
        INNER JOIN 
            location l ON w.workshop_location = l.location_id
        WHERE workshop_attendance > 0 and w.workshop_date between %s and %s
        ORDER BY workshop_date asc;"""
        cursor.execute(sql, (dateFrom, dateTo,))
        workshops = cursor.fetchall()

        sql = """
        SELECT 
            l.lesson_id AS lesson_id,
            CONCAT(s.staff_title, ' ', s.staff_firstname, ' ', s.staff_familyname) AS tutor,
            li.lesson_info_type AS lesson_topic,
            l.lesson_detail AS lesson_detail,
            l.lesson_date AS lesson_date,
            TIME_FORMAT(l.lesson_start_time, '%h:%i %p') AS lesson_time,
           loc.location_name AS lesson_location,
            l.lesson_attendance AS lesson_attendance
        FROM 
            lesson l
        INNER JOIN 
            staff s ON l.lesson_tutor_id = s.staff_id
        INNER JOIN 
            lesson_info li ON l.lesson_title_id = li.lesson_info_id
        INNER JOIN 
            location loc ON l.lesson_location = loc.location_id
		WHERE lesson_attendance > 0 and l.lesson_date between %s and %s
        ORDER BY lesson_date asc;"""
        cursor.execute(sql, (dateFrom, dateTo,))
        lessons = cursor.fetchall()

    else:
        sql = """
            SELECT 
                w.workshop_id AS workshop_id,
                CONCAT(s.staff_title, ' ', s.staff_firstname, ' ', s.staff_familyname) AS tutor,
                wi.workshop_info_topic AS workshop_topic,
                wi.workshop_info_desc AS workshop_detail,
                w.workshop_date AS workshop_date,
                TIME_FORMAT(w.workshop_time, '%h:%i %p') AS workshop_time,
                CONCAT(l.location_name, ' ', l.location_description) AS workshop_location,
                w.workshop_attendance AS workshop_attendance
            FROM 
                workshop w
            INNER JOIN 
                staff s ON w.workshop_tutor_id = s.staff_id
            INNER JOIN 
                workshop_info wi ON w.workshop_title_id = wi.workshop_info_id
            INNER JOIN 
                location l ON w.workshop_location = l.location_id
            WHERE workshop_attendance > 0
            ORDER BY workshop_attendance DESC;
                """   
        cursor.execute(sql)
        workshops = cursor.fetchall()

        sql = """
        SELECT 
            l.lesson_id AS lesson_id,
            CONCAT(s.staff_title, ' ', s.staff_firstname, ' ', s.staff_familyname) AS tutor,
            li.lesson_info_type AS lesson_topic,
            l.lesson_detail AS lesson_detail,
            l.lesson_date AS lesson_date,
            TIME_FORMAT(l.lesson_start_time, '%h:%i %p') AS lesson_time,
           loc.location_name AS lesson_location,
            l.lesson_attendance AS lesson_attendance
        FROM 
            lesson l
        INNER JOIN 
            staff s ON l.lesson_tutor_id = s.staff_id
        INNER JOIN 
            lesson_info li ON l.lesson_title_id = li.lesson_info_id
        INNER JOIN 
            location loc ON l.lesson_location = loc.location_id
		WHERE lesson_attendance > 0
        ORDER BY lesson_date asc;"""
        cursor.execute(sql)
        lessons = cursor.fetchall()

    workshop_titles = [workshop[2] for workshop in workshops]
    attendance_data = [workshop[7] for workshop in workshops]
    time_formatted = [workshop[5] for workshop in workshops]
    workshop_details = [f"Date: {workshop[4].strftime('%d-%m-%Y')}, Time: {time}, Tutor: {workshop[1]}" for workshop, time in zip(workshops, time_formatted)]

    lesson_titles = [lesson[2] for lesson in lessons]
    lesson_attendance_data = [lesson[7] for lesson in lessons]
    lesson_time_formatted = [lesson[5] for lesson in lessons]
    lesson_details = [f"Date: {lesson[4].strftime('%d-%m-%Y')}, Time: {time}, Tutor: {lesson[1]}" for lesson, time in zip(lessons, lesson_time_formatted)]


    cursor, connection = getCursor()

    #below workshop and lesson sections retrieved information to be used in the template
    #there is 2 filters available to be checked
    #1st is to filter by workshop and lesson
    #2nd is to filter by the date from and date to
    #in the where criteria, the bookings booked = true and lesson/workshop attendance > 0
    if filter == "lesson":

        if show =="show":
            cursor.execute("""SELECT l.lesson_id, l.lesson_date, TIME_FORMAT(l.lesson_start_time, '%h:%i %p') AS formatted_start_time,
                                li.lesson_info_type, l.lesson_detail, loc.location_name, loc.location_description, loc.location_map,
                                loc.location_limit, l.lesson_tutor_id, (select count(*)  from booking where booking_lesson_id = l.lesson_id) as number_booked, 
                                lesson_attendance
                            FROM lesson l
                            JOIN 
                                lesson_info li ON l.lesson_title_id = li.lesson_info_id
                            JOIN 
                                location loc ON l.lesson_location = loc.location_id
                            WHERE 
                                l.lesson_booked = true and lesson_attendance > 0 and lesson_date between %s and %s order by lesson_date asc;""",(dateFrom, dateTo,))
        else:
            cursor.execute("""SELECT l.lesson_id, l.lesson_date, TIME_FORMAT(l.lesson_start_time, '%h:%i %p') AS formatted_start_time,
                    li.lesson_info_type, l.lesson_detail, loc.location_name, loc.location_description, loc.location_map,
                    loc.location_limit, l.lesson_tutor_id, (select count(*)  from booking where booking_lesson_id = l.lesson_id) as number_booked, 
                    lesson_attendance
                FROM lesson l
                JOIN 
                    lesson_info li ON l.lesson_title_id = li.lesson_info_id
                JOIN 
                    location loc ON l.lesson_location = loc.location_id
                WHERE 
                    l.lesson_booked = true and lesson_attendance > 0 order by lesson_date asc;""")
        
        lesson = cursor.fetchall()
        return render_template('manager_patterns.html', filter="lesson", lesson=lesson, workshops=workshops, workshop_titles=workshop_titles, attendance_data=attendance_data, workshop_details=workshop_details,lessons=lessons, lesson_titles=lesson_titles, lesson_attendance_data=lesson_attendance_data, lesson_details=lesson_details)

    else:

        if show =="show":
            cursor.execute("""SELECT l.workshop_id, l.workshop_date, TIME_FORMAT(l.workshop_time, '%h:%i %p') AS formatted_start_time,
                                    li.workshop_info_topic, l.workshop_detail, loc.location_name, loc.location_description, loc.location_map,
                                    l.workshop_cap_limit, l.workshop_tutor_id, (select count(*)  from booking where booking_workshop_id = l.workshop_id) as number_booked, 
                                    workshop_attendance
                                FROM workshop l
                                JOIN 
                                    workshop_info li ON l.workshop_title_id = li.workshop_info_id
                                JOIN 
                                    location loc ON l.workshop_location = loc.location_id
                                WHERE workshop_attendance > 0 and workshop_date between %s and %s
                                order by workshop_date asc;""",(dateFrom, dateTo,))
        else: 
            cursor.execute("""SELECT l.workshop_id, l.workshop_date, TIME_FORMAT(l.workshop_time, '%h:%i %p') AS formatted_start_time,
                                li.workshop_info_topic, l.workshop_detail, loc.location_name, loc.location_description, loc.location_map,
                                l.workshop_cap_limit, l.workshop_tutor_id, (select count(*)  from booking where booking_workshop_id = l.workshop_id) as number_booked, 
                                workshop_attendance
                            FROM workshop l
                            JOIN 
                                workshop_info li ON l.workshop_title_id = li.workshop_info_id
                            JOIN 
                                location loc ON l.workshop_location = loc.location_id
                            WHERE workshop_attendance > 0 
                            order by workshop_date asc;""")
            
        workshop = cursor.fetchall()
        return render_template('manager_patterns.html', filter="workshop", workshop=workshop, workshops=workshops, workshop_titles=workshop_titles, attendance_data=attendance_data, workshop_details=workshop_details,lessons=lessons, lesson_titles=lesson_titles, lesson_attendance_data=lesson_attendance_data, lesson_details=lesson_details)



@app.route('/newslist', methods=['GET', 'POST'])
@logged_in
def newslist():
    cursor, connection = getCursor()
    cursor.execute("SELECT * FROM news ORDER BY news_uploaded DESC")
    newslist = cursor.fetchall()
    closeConnection()
    return render_template("news_list.html", news_list = newslist)

@app.route('/addnews', methods=['GET', 'POST'])
@logged_in
def addnews():
    cursor, connection = getCursor()
    form = NewsForm()
    if form.validate_on_submit():
        title = form.title.data
        text = form.text.data
        images = form.images.data  # Assuming you're storing image paths in the database
        # Handle image uploads
        uploaded_files = request.files.getlist('images')
        for file in uploaded_files:
            if file.filename != '':
                random_string = str(uuid.uuid4())[:8]  
                new_filename = random_string + '_' + secure_filename(file.filename)
                file_path = os.path.join('app', 'static/images', new_filename)
                file.save(file_path)
                # Save the image filename or path to the database
        newsdate = datetime.now()  # Set current date and time
        # Insert the news data into the database
        cursor.execute("INSERT INTO news (new_title, news_text, news_image, news_uploaded) VALUES (%s, %s, %s, %s)",
                    (title, text, new_filename, newsdate))
        connection.commit()
        closeConnection()
        flash('News added successfully!', 'success')  # Flash a success message
        return redirect(url_for('newslist'))  # Redirect to the add news page
    return render_template('add_news.html', form=form, current_datetime=datetime.now())

@app.route('/deletenews', methods=['POST'])
@logged_in
def deletenews():
    #function to delete news
    #news ID retrieved from caller form
    #caller: newslist.html
    cursor, connection = getCursor()

    news_id = int(request.form.get('newsID'))

    cursor.execute("""delete from news where news_id = %s;""",
            (news_id,))
    
    connection.commit()
    closeConnection()
    
    flash(f'News deleted successfully', category='success')

    closeConnection()
    return redirect("/newslist")

@app.route("/editnews/<int:newsid>", methods=['GET', 'POST'])
@logged_in
def editnews(newsid):
    form = EditNewsForm()
    cursor, connection = getCursor()
    cursor.execute('SELECT * FROM news WHERE news_id = %s', (newsid,))
    news = cursor.fetchone()
    
    if not news:
        flash('News not found', 'error')
        return redirect(url_for('newslist'))

    if request.method == 'POST' and form.validate_on_submit():
        title = form.title.data
        text = form.text.data
        images = form.images.data
        # Save uploaded files to server and database
        if images is not None:
            for idx, file in enumerate(images):
                random_string = str(uuid.uuid4())[:8]  # Using UUID for randomness
                new_filename = random_string + '_' + secure_filename(file.filename)
                file_path = os.path.join('app', 'static/images', new_filename)
                file.save(file_path)
                cursor, connection = getCursor()
                cursor.execute('Update news Set news_image = %s WHERE news_id = %s;', 
                            (new_filename, newsid,))
                connection.commit()

        # Logic for deleting images
        selected_options = request.form.getlist('option')
        for option in selected_options:
            imagepath = os.path.join('app', 'static/images', option)
            # Check if the file exists before attempting to delete it
            if os.path.exists(imagepath):
                # Delete the file
                os.remove(imagepath)
                cursor, connection = getCursor()
                cursor.execute("""Update news Set news_image = NULL WHERE news_id = %s;""",
                            (newsid,))
                connection.commit()

        newsdate = datetime.now()
        cursor.execute('UPDATE news SET new_title = %s, news_text = %s, news_uploaded = %s WHERE news_id = %s',
               (title, text, newsdate, newsid))
        connection.commit()
        
        flash('News updated successfully', 'success')
        return redirect(url_for('newslist'))

    form.title.data = news[1]
    form.text.data = news[2]
    if news[3] is not None:
        form.images.choices = [news[3]]
    else:
        form.images.choices = []  # or any other default value you want to set

    closeConnection()
    return render_template("edit_news.html", form=form, news_id=newsid)


@app.route("/revenue", methods=['GET', 'POST'])
@logged_in
def revenue():
    if request.method == 'POST':
        year = request.form['year']
        cursor, connection = getCursor()
        # Execute the SQL query to get the revenue filtered by year
        #SQL query will perform the calculation and adding up of the payment_amount and sort them into corresponding revenuews
        # it will also group the calculated payment amount into months 
        query = """SELECT 
                    months.month AS month,
                    COALESCE(SUM(CASE WHEN payment_subscription_id is not null THEN payment_amount ELSE 0 END), 0) AS subscription_revenue,
                    COALESCE(SUM(CASE WHEN payment_workshop_id is not null THEN payment_amount ELSE 0 END), 0) AS workshop_revenue,
                    COALESCE(SUM(CASE WHEN payment_lesson_id is not null THEN payment_amount ELSE 0 END), 0) AS lesson_revenue,
                    COALESCE(SUM(payment_amount), 0) AS total_revenue
                FROM (
                    SELECT 1 AS month UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION
                    SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10 UNION SELECT 11 UNION SELECT 12
                ) AS months
                LEFT JOIN payment ON months.month = MONTH(payment_date) AND YEAR(payment_date) = %s
                GROUP BY month"""
        cursor.execute(query, (year,))

        revenue_report = {}
            
        #below loop will sort the list into proper array to tbe easily displayed in the format that we wanted in the template
        for row in cursor.fetchall():
            month = row[0]
            month_name = calendar.month_name[month] 
            subscription_revenue = row[1]
            workshop_revenue = row[2]
            lesson_revenue = row[3]
            total_revenue = row[4]
            
            revenue_report[month_name] = {
                'Subscription': subscription_revenue,
                'Workshop': workshop_revenue,
                'Lesson': lesson_revenue,
                'Total': total_revenue
            }
        
        cursor.close()
        return render_template('revenue.html', year=year, revenue_report=revenue_report)
    else:
        return render_template('revenue.html')



# manage tutor lesson schedules
    
@app.route('/alltutorlessons')
@logged_in
def alltutorlessons():
    # function will return all the tutor lessons
    # these will be all the upcoming lessons
    cursor, connection = getCursor()
    cursor.execute("""SELECT 
                lesson.lesson_id,
                lesson.lesson_title_id,
                lesson_info.lesson_info_type AS lesson_title,
                CONCAT(staff.staff_title, ' ', staff.staff_firstname, ' ', staff.staff_familyname) AS tutor_name,
                location.location_name AS location,
                lesson.lesson_date AS Date,
                TIME_FORMAT(lesson.lesson_start_time, '%h:%i %p') AS Time,
                CASE
                    WHEN lesson.lesson_booked = true THEN 'Yes'
                    ELSE 'No'
                END AS Scheduled,
                lesson.lesson_detail AS Detail
            FROM 
                lesson
            JOIN 
                lesson_info ON lesson.lesson_title_id = lesson_info.lesson_info_id
            JOIN 
                staff ON lesson.lesson_tutor_id = staff.staff_id
            JOIN 
                location ON lesson.lesson_location = location.location_id
            WHERE lesson.lesson_date > curdate() order by lesson.lesson_date asc;""")
    alltutorlessons = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template("all_tutor_lessons.html", alltutorlessons = alltutorlessons)



# delete a lesson
@app.route('/deleteatutorlesson', methods=['POST'])
@logged_in
def deleteatutorlesson():
    # function to delete a tutor lesson
    # lesson ID retrieved from caller form
    # caller: all_tutor_lessons.html
    cursor, connection = getCursor()

    lesson_id = int(request.form.get('lesson_id'))

    # Check if there are any bookings/payments associated with this lesson
    cursor.execute("""SELECT * FROM booking WHERE booking_lesson_id = %s""", (lesson_id,))
    bookings = cursor.fetchall()

    cursor.execute("""SELECT * FROM payment WHERE payment_lesson_id = %s""", (lesson_id,))
    payments = cursor.fetchall()


    # If there are bookings/payments, delete them first
    if bookings:
        cursor.execute("""DELETE FROM booking WHERE booking_lesson_id = %s""", (lesson_id,))
    if payments:
        cursor.execute("""DELETE FROM payment WHERE payment_lesson_id = %s""", (lesson_id,))

    cursor.execute("""DELETE FROM lesson WHERE lesson_id = %s""", (lesson_id,))
    flash(f'Lesson deleted successfully', category='success')
    
    connection.commit()
    connection.close()

    return redirect("/alltutorlessons")

# add a lesson 
@app.route('/addalesson')
@logged_in
def addalesson():
    form = AddaLessonForm()

    cursor, connection = getCursor()

    # Fetch titles from MySQL
    cursor.execute("SELECT lesson_info_id, lesson_info_type FROM lesson_info;")
    titles = cursor.fetchall()

    cursor.execute("SELECT location_id, location_name FROM location;")
    locations = cursor.fetchall()

    cursor.execute("""SELECT 
                   s.staff_id, s.staff_title, s.staff_firstname, s.staff_familyname 
                   FROM staff s 
                   INNER JOIN user u ON s.staff_id = u.user_id 
                   WHERE u.userrole = 'TT';""")
    tutors = cursor.fetchall()
    default_tutor_id = str(tutors[0][0])

    form.title.choices = titles
    form.location.choices = locations
    form.tutor.choices = [(str(tutor[0]), f"{tutor[1]} {tutor[2]} {tutor[3]}") for tutor in tutors]
    

    cursor.execute("SELECT lesson_info_id, lesson_info_type, lesson_info_desc FROM lesson_info;")
    titles = cursor.fetchall()
    # Convert the titles data to a list of dictionaries
    titles_data = [{'id': title[0], 'type': title[1], 'desc': title[2]} for title in titles]

    # Create form and populate choices
    cursor.close()
    connection.close()

    return render_template('manager_add_lesson.html', form=form, titles_data=titles_data, default_tutor_id=default_tutor_id)

@app.route('/insertalesson', methods=['POST'])
@logged_in
def insertalesson():
    #function to create a lesson
    msg=''
    form=AddaLessonForm()

    cursor, connection = getCursor()

    # Fetch data from MySQL
    cursor.execute("SELECT lesson_info_id, lesson_info_type FROM lesson_info;")
    titles = cursor.fetchall()

    cursor.execute("SELECT location_id, location_name FROM location;")
    locations = cursor.fetchall()

    cursor.execute("""SELECT 
                   s.staff_id, s.staff_title, s.staff_firstname, s.staff_familyname 
                   FROM staff s 
                   INNER JOIN user u ON s.staff_id = u.user_id 
                   WHERE u.userrole = 'TT';""")
    tutors = cursor.fetchall()


    # Close cursor and connection
    cursor.close()
    connection.close()

    # Create form and populate choices
    form.title.choices = titles
    form.location.choices = locations
    form.tutor.choices = [(str(tutor[0]), f"{tutor[1]} {tutor[2]} {tutor[3]}") for tutor in tutors]


    if form.validate_on_submit():
        lessontitle = form.title.data
        lessonlocation = form.location.data
        lessondate = form.lessondate.data
        lessonstarttime = form.lessonstarttime.data
        lessondesc = form.lessondesc.data
        lessontutor = form.tutor.data

        cursor, connection = getCursor()
        #check for timetable clashes
        #get the workshop and lesson of the tutor and the date and time from the new lesson to be created
        cursor.execute('select * from workshop where workshop_tutor_id = %s and workshop_date = %s and workshop_time=%s',
                            ( lessontutor, lessondate, lessonstarttime, ))
        workshop_clash = cursor.fetchone()

        cursor.execute('select * from lesson where lesson_tutor_id = %s and lesson_date = %s and lesson_start_time = %s',
                    ( lessontutor, lessondate, lessonstarttime, ))
        lesson_clash = cursor.fetchone()

        if workshop_clash is None and lesson_clash is None:
            cursor.execute('INSERT INTO lesson (lesson_title_id, lesson_tutor_id, lesson_location, lesson_date, lesson_start_time, lesson_detail ) VALUES ( %s, %s, %s, %s, %s, %s)',
                            (lessontitle, lessontutor, lessonlocation, lessondate, lessonstarttime, lessondesc, ))
            connection.commit()

            flash(f'Lesson created successfully', category='success')
            #once registration is successful, user will be routed to the login screen
            connection.close()
            return redirect(url_for('alltutorlessons'))
        else: 
            msg = "Failed to create lesson due to timetable clash"
            return render_template('manager_add_lesson.html', title='Add New Lesson', form=form, msg=msg)
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show create lesson form with message (if any)
    connection.close()
    return render_template('manager_add_lesson.html', title='Add New Lesson', form=form, msg=msg)


# edit a lesson
@app.route("/editalesson/<lessonid>", methods=["GET"])
@logged_in
def editalesson(lessonid):
    #function to retrieve tutor lesson for editing
    #lesson ID passed in via hyperlink
    #caller: all_tutor_lessons.html
    form=EditaLessonForm()

    cursor, connection = getCursor()

    # Fetch data from MySQL
    cursor.execute("SELECT lesson_info_id, lesson_info_type FROM lesson_info;")
    titles = cursor.fetchall()

    cursor.execute("SELECT location_id, location_name FROM location;")
    locations = cursor.fetchall()

    cursor.execute("""SELECT 
                   s.staff_id, s.staff_title, s.staff_firstname, s.staff_familyname 
                   FROM staff s 
                   INNER JOIN user u ON s.staff_id = u.user_id 
                   WHERE u.userrole = 'TT';""")
    tutors = cursor.fetchall()

    # Create form and populate choices
    form.title.choices = [(str(title[0]), title[1]) for title in titles]
    form.location.choices = [(str(location[0]), location[1]) for location in locations]
    form.tutor.choices = [(str(tutor[0]), f"{tutor[1]} {tutor[2]} {tutor[3]}") for tutor in tutors]


    cursor.execute('SELECT * FROM lesson WHERE lesson_id = %s', (lessonid,) )
    lessonList = cursor.fetchall()

    # Set default values
    default_title_id = str(lessonList[0][1])
    default_location_id = str(lessonList[0][3])
    default_tutor_id = str(lessonList[0][2])

    # Find default values in choices and set them
    form.title.data = next((id for id, _ in form.title.choices if id == default_title_id), None)
    form.location.data = next((id for id, _ in form.location.choices if id == default_location_id), None)
    form.tutor.data = next((id for id, _ in form.tutor.choices if id == default_tutor_id), None)
    
    form.lessondate.data = lessonList[0][4]
    form.lessondesc.data = lessonList[0][7]

    if lessonList[0][5] is None:
        start_time = time(0, 0)  # Assign a default time, e.g., midnight
    else:
        time_str = str(lessonList[0][5])
        if time_str == '0:00:00':
            start_time = time(0, 0)
        else:
            start_time = time.fromisoformat(time_str)
    form.lessonstarttime.data = start_time

    # prepare data for auto fill javascript function
    cursor.execute("SELECT lesson_info_id, lesson_info_type, lesson_info_desc FROM lesson_info;")
    titles = cursor.fetchall()
    # Convert the titles data to a list of dictionaries
    titles_data = [{'id': title[0], 'type': title[1], 'desc': title[2]} for title in titles]

    connection.close()
    return render_template("manager_edit_lesson.html", form=form, lesson_id = lessonid, titles_data=titles_data)


@app.route('/updatealesson', methods=['POST'])
@logged_in
def updatealesson():
    #function to edit lesson
    msg=''
    form=EditaLessonForm()

    cursor, connection = getCursor()

    # Fetch data from MySQL
    cursor.execute("SELECT lesson_info_id, lesson_info_type FROM lesson_info;")
    titles = cursor.fetchall()

    cursor.execute("SELECT location_id, location_name FROM location;")
    locations = cursor.fetchall()

    cursor.execute("""SELECT 
                   s.staff_id, s.staff_title, s.staff_firstname, s.staff_familyname 
                   FROM staff s 
                   INNER JOIN user u ON s.staff_id = u.user_id 
                   WHERE u.userrole = 'TT';""")
    tutors = cursor.fetchall()

    # Create form and populate choices
    form.title.choices = [(str(title[0]), title[1]) for title in titles]
    form.location.choices = [(str(location[0]), location[1]) for location in locations]
    form.tutor.choices = [(str(tutor[0]), f"{tutor[1]} {tutor[2]} {tutor[3]}") for tutor in tutors]

    if form.validate_on_submit():

        lesson_id = request.form.get('lesson_id')
        title = form.title.data
        location = form.location.data
        lessondate = form.lessondate.data
        lessonstarttime = form.lessonstarttime.data
        lessondesc = form.lessondesc.data
        tutor = form.tutor.data

        cursor.execute("""select * from workshop where workshop_tutor_id = %s 
                            and workshop_date = %s and workshop_time=%s""",
                            ( tutor, lessondate, lessonstarttime, ))
        workshop_clash = cursor.fetchone()

        cursor.execute("""select * from lesson where lesson_tutor_id = %s 
                            and lesson_date = %s and lesson_start_time = %s and lesson_id <> %s""",
                    ( tutor, lessondate, lessonstarttime, lesson_id, ))
        lesson_clash = cursor.fetchone()

        #check if there is a timetable clash in workshop and lesson
        if workshop_clash is None and lesson_clash is None:

            cursor.execute("""UPDATE lesson SET lesson_title_id=%s,lesson_tutor_id=%s, lesson_location= %s, 
                        lesson_date =%s, lesson_start_time =%s, lesson_detail=%s
                        WHERE lesson_id = %s;""",
                                ( title, tutor, location, lessondate, lessonstarttime, lessondesc, lesson_id, ))

            flash('Lesson updated successfully', category='success')
            connection.close()
            return redirect("/alltutorlessons")
        else: 
            msg = "Failed to edit lesson due to timetable clash"
            return render_template('manager_edit_lesson.html', title='Edit Lesson', form=form, msg=msg)
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    connection.close()
    return render_template('manager_edit_lesson.html', title='Edit Lesson', form=form, msg=msg)

  
@app.route('/manage_workshop_list')
@logged_in
def manage_workshop_list():
    # Get the current date
    current_date = datetime.now().date()

    # Function to retrieve and display all the upcoming workshop list
    cursor, connection = getCursor()
    cursor.execute("""
        SELECT 
            w.workshop_id,
            wi.workshop_info_topic,
            s.staff_id AS tutor_id,
            CONCAT(s.staff_title, ' ',s.staff_firstname, ' ', s.staff_familyname) AS tutor_name,
            w.workshop_detail,
            w.workshop_date,
            TIME_FORMAT(w.workshop_time, '%h:%i %p') AS workshop_time,
            l.location_name,
            l.location_description AS workshop_location,
            w.workshop_cost,
            w.workshop_cap_limit,
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
            w.workshop_date >= %s
        ORDER BY 
            workshop_date ASC
    """, (current_date,))
    workshop_list = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template("manage_workshop_list.html", workshop_list=workshop_list)


@app.route('/manage_weekly_workshop_list')
@logged_in
def manage_weekly_workshop_list():
    # Get the current date
    current_date = datetime.now().date()

    # Calculate end date for filtering (7 days from now)
    end_date = current_date + timedelta(days=7)

    # Function to retrieve and display all the upcoming workshop list
    cursor, connection = getCursor()
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
            w.workshop_cap_limit,
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
            w.workshop_date BETWEEN %s AND %s
        ORDER BY 
            workshop_date ASC
    """, (current_date, end_date))
    workshop_list = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template("manage_weekly_workshop_list.html", workshop_list=workshop_list)

@app.route('/addworkshop', methods=['GET', 'POST'])
@logged_in 
def add_workshop():
    if request.method == 'POST':
        workshop_topic = request.form['workshop_topic']
        workshop_detail = request.form['workshop_detail']
        workshop_date = request.form['workshop_date']
        workshop_time = request.form['workshop_time']
        workshop_tutor_id = request.form['workshop_tutor_id']
        workshop_location = request.form['workshop_location']
        workshop_cost = request.form['workshop_cost']
        workshop_cap_limit = request.form['workshop_cap_limit']

        # Convert workshop_date and workshop_time to a datetime object for comparison
        workshop_start_time = datetime.strptime(workshop_date + ' ' + workshop_time, '%Y-%m-%d %H:%M')
        workshop_end_time = workshop_start_time + timedelta(hours=2)  # Workshop duration is 2 hours

        try:
            cursor, connection = getCursor()
            # Check if the selected tutor is already assigned to a workshop within the specified time range
            cursor.execute("""
                SELECT COUNT(*) 
                FROM workshop 
                WHERE workshop_tutor_id = %s 
                AND workshop_date = %s 
                AND workshop_time BETWEEN %s AND %s
            """, (workshop_tutor_id, workshop_date, workshop_time, workshop_end_time))
            tutor_workshops_count = cursor.fetchone()[0]
            
            if tutor_workshops_count > 0:
                flash('Tutor already has a workshop scheduled at this time. Please select another tutor.')
                return redirect(request.url)
            
            cursor.execute("""
                INSERT INTO workshop (workshop_title_id, workshop_detail, workshop_date, workshop_time, workshop_tutor_id, workshop_location, workshop_cost, workshop_cap_limit)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (workshop_topic, workshop_detail, workshop_date, workshop_time, workshop_tutor_id, workshop_location, workshop_cost, workshop_cap_limit))
            connection.commit()
            cursor.close()
            connection.close()
            return redirect(url_for('manage_workshop_list'))
        except mysql.connector.Error as error:
            print("Failed to insert record into MySQL table:", error)

    # If request method is GET or if there was an error in POST request, render the add workshop form
    cursor, connection = getCursor()
    cursor.execute("SELECT workshop_info_id, workshop_info_topic, workshop_info_desc FROM workshop_info")
    workshop_info = cursor.fetchall()
    cursor.execute("""
        SELECT s.staff_id, s.staff_title, CONCAT(s.staff_firstname, ' ', s.staff_familyname) AS tutor_name 
        FROM staff s
        JOIN user u ON s.staff_id = u.user_id
        WHERE u.userrole = 'TT'
    """)
    tutors = cursor.fetchall()
    cursor.execute("SELECT location_id, location_name FROM location")
    locations = cursor.fetchall()
    cursor.close()
    connection.close()
    
    return render_template('add_workshop.html', workshop_info=workshop_info, tutors=tutors, locations=locations)


@app.route("/editworkshop/<int:workshop_id>", methods=["GET", "POST"])
@logged_in
def edit_workshop(workshop_id):
    if request.method == "GET":
        # Fetch workshop details from the database
        cursor, connection = getCursor()
        cursor.execute("""
            SELECT 
                w.workshop_id,
                wi.workshop_info_topic,
                s.staff_id AS tutor_id,
                CONCAT(s.staff_title, ' ', s.staff_firstname, ' ', s.staff_familyname) AS tutor_name,
                w.workshop_detail,
                w.workshop_date,
                TIME_FORMAT(w.workshop_time, '%H:%i') AS workshop_time,
                l.location_name,
                l.location_description AS workshop_location,
                w.workshop_cost,
                w.workshop_cap_limit
            FROM 
                workshop w
            JOIN 
                staff s ON w.workshop_tutor_id = s.staff_id
            JOIN 
                workshop_info wi ON w.workshop_title_id = wi.workshop_info_id
            JOIN 
                location l ON w.workshop_location = l.location_id
            WHERE
                w.workshop_id = %s
            """, (workshop_id,))
        workshop = cursor.fetchone()
        
        # Fetch data for workshop topics, tutors, and locations
        cursor.execute("SELECT workshop_info_id, workshop_info_topic FROM workshop_info")
        workshop_info = cursor.fetchall()
        cursor.execute("""
            SELECT s.staff_id, s.staff_title, CONCAT(s.staff_firstname, ' ', s.staff_familyname) AS tutor_name 
            FROM staff s
            JOIN user u ON s.staff_id = u.user_id
            WHERE u.userrole = 'TT'
        """)
        tutors = cursor.fetchall()
        cursor.execute("SELECT location_id, location_name FROM location")
        locations = cursor.fetchall()
        
        cursor.close()
        connection.close()

        if workshop:
            # Render the edit workshop form with pre-filled data
            return render_template("edit_workshop.html", workshop=workshop, workshop_info=workshop_info, tutors=tutors, locations=locations)
        else:
            flash("Workshop not found!", "error")
            return redirect(url_for("manage_workshop_list"))
    elif request.method == "POST":
        # Process form submission to update workshop details in the database
        # Retrieve form data
        workshop_detail = request.form["workshop_detail"]
        workshop_date = request.form["workshop_date"]
        workshop_time = request.form["workshop_time"]
        workshop_tutor_id = request.form["workshop_tutor_id"]
        workshop_location = request.form["workshop_location"]
        workshop_cost = request.form["workshop_cost"]
        workshop_cap_limit = request.form["workshop_cap_limit"]

        # Check tutor availability
        try:
            cursor, connection = getCursor()
            # Check if the selected tutor is already assigned to a workshop within the specified time range (excluding the current workshop being edited)
            cursor.execute("""
                SELECT COUNT(*) 
                FROM workshop 
                WHERE workshop_tutor_id = %s 
                AND workshop_date = %s 
                AND workshop_time BETWEEN %s AND ADDTIME(%s, '02:00:00')
                AND workshop_id != %s
            """, (workshop_tutor_id, workshop_date, workshop_time, workshop_time, workshop_id))
            tutor_workshops_count = cursor.fetchone()[0]
            
            if tutor_workshops_count > 0:
                flash('Tutor already has a workshop scheduled during this time. Please select another tutor.', category='warning')
                return redirect(url_for("edit_workshop", workshop_id=workshop_id))
            
            # Update workshop details in the database
            cursor.execute("""
                UPDATE workshop 
                SET 
                    workshop_detail = %s,
                    workshop_date = %s,
                    workshop_time = %s,
                    workshop_tutor_id = %s,
                    workshop_location = %s,
                    workshop_cost = %s,
                    workshop_cap_limit = %s
                WHERE 
                    workshop_id = %s
                """, (workshop_detail, workshop_date, workshop_time, workshop_tutor_id, workshop_location, workshop_cost, workshop_cap_limit, workshop_id))
            connection.commit()
            cursor.close()
            connection.close()
            flash("Workshop updated successfully!", "success")
            return redirect(url_for("manage_workshop_list"))
        except mysql.connector.Error as error:
            flash(f"Failed to update workshop: {error}", "error")
            return redirect(url_for("manage_workshop_list"))
        

@app.route("/deleteworkshop", methods=["POST"])
@logged_in
def delete_workshop():
    if request.method == "POST":
        workshop_id = request.form.get("workshopID")

        try:
            cursor, connection = getCursor()
            
            # Manually delete related records in the payment table
            cursor.execute("DELETE FROM payment WHERE payment_workshop_id = %s", (workshop_id,))
            
            # Then delete related records in the booking table
            cursor.execute("DELETE FROM booking WHERE booking_workshop_id = %s", (workshop_id,))
            
            # Then delete the workshop
            cursor.execute("DELETE FROM workshop WHERE workshop_id = %s", (workshop_id,))
            
            connection.commit()
            cursor.close()
            connection.close()
            flash("Workshop deleted successfully!", "success")
        except mysql.connector.Error as error:
            flash(f"Failed to delete workshop: {error}", "error")

    return redirect(url_for("manage_workshop_list"))

# view payment reports

@app.route('/trackpayment', methods=['GET', 'POST'])
@logged_in
def trackpayment():
    filter = request.form.get('filter')
    cursor, connection = getCursor()

    #payment reports can be filtered by lesson/workshop/subscription
    if filter == "lesson":
        cursor.execute("""select payment_date, payment_amount, 
                                CASE
                                        WHEN payment_workshop_id IS NOT NULL THEN 'Workshop'
                                        WHEN payment_lesson_id IS NOT NULL THEN 'Lesson'
                                        WHEN payment_subscription_id IS NOT NULL THEN 'Subscription'
                                END AS payment_for,
                            member_title, member_firstname, member_familyname, 
                            member_phonenumber, member_email, member_address, member_dob, member_position
                            from payment a, member b
                            where a.payment_payor_id = b.member_id and a.payment_lesson_id is not null order by payment_date asc;""")
        lesson = cursor.fetchall()
        return render_template('manage_payment.html', filter="lesson", lesson=lesson)

    elif filter == "workshop":
        cursor.execute("""select payment_date, payment_amount, 
                                CASE
                                        WHEN payment_workshop_id IS NOT NULL THEN 'Workshop'
                                        WHEN payment_lesson_id IS NOT NULL THEN 'Lesson'
                                        WHEN payment_subscription_id IS NOT NULL THEN 'Subscription'
                                END AS payment_for,
                            member_title, member_firstname, member_familyname, 
                            member_phonenumber, member_email, member_address, member_dob, member_position
                            from payment a, member b
                            where a.payment_payor_id = b.member_id and a.payment_workshop_id is not null order by payment_date asc;""")
        workshop = cursor.fetchall()
        return render_template('manage_payment.html', filter="workshop", workshop=workshop)
    
    elif filter == "subscription":
        cursor.execute("""select payment_date, payment_amount, 
                                CASE
                                        WHEN payment_workshop_id IS NOT NULL THEN 'Workshop'
                                        WHEN payment_lesson_id IS NOT NULL THEN 'Lesson'
                                        WHEN payment_subscription_id IS NOT NULL THEN 'Subscription'
                                END AS payment_for,
                            member_title, member_firstname, member_familyname, 
                            member_phonenumber, member_email, member_address, member_dob, member_position
                            from payment a, member b
                            where a.payment_payor_id = b.member_id and a.payment_subscription_id is not null order by payment_date asc;""")
        subscription = cursor.fetchall()
        return render_template('manage_payment.html', filter="subscription", subscription=subscription)

    else:
        #default is to select all payments
        cursor.execute("""select payment_date, payment_amount, 
                                CASE
                                        WHEN payment_workshop_id IS NOT NULL THEN 'Workshop'
                                        WHEN payment_lesson_id IS NOT NULL THEN 'Lesson'
                                        WHEN payment_subscription_id IS NOT NULL THEN 'Subscription'
                                END AS payment_for,
                            member_title, member_firstname, member_familyname, 
                            member_phonenumber, member_email, member_address, member_dob, member_position
                            from payment a, member b
                            where a.payment_payor_id = b.member_id order by payment_date asc;""")
        payment = cursor.fetchall()
        today = date.today()
        return render_template('manage_payment.html', payment=payment, today=today)

@app.route('/trackattendance', methods=['GET', 'POST'])
@logged_in
def trackattendance():
    filter = request.form.get('filter')
    cursor, connection = getCursor()
    #select lessons and workshops which has been booked
    if filter == "lesson":
        cursor.execute("""SELECT l.lesson_id, l.lesson_date, TIME_FORMAT(l.lesson_start_time, '%h:%i %p') AS formatted_start_time,
                            li.lesson_info_type, l.lesson_detail, loc.location_name, loc.location_description, loc.location_map,
                            loc.location_limit, l.lesson_tutor_id, (select count(*)  from booking where booking_lesson_id = l.lesson_id) as number_booked, 
                            lesson_attendance
                        FROM lesson l
                        JOIN 
                            lesson_info li ON l.lesson_title_id = li.lesson_info_id
                        JOIN 
                            location loc ON l.lesson_location = loc.location_id
                        WHERE 
                            l.lesson_booked = true order by lesson_date asc;""")
        lesson = cursor.fetchall()
        return render_template('manage_attendance.html', filter="lesson", lesson=lesson)

    else:
        cursor.execute("""SELECT l.workshop_id, l.workshop_date, TIME_FORMAT(l.workshop_time, '%h:%i %p') AS formatted_start_time,
                                li.workshop_info_topic, l.workshop_detail, loc.location_name, loc.location_description, loc.location_map,
                                l.workshop_cap_limit, l.workshop_tutor_id, (select count(*)  from booking where booking_workshop_id = l.workshop_id) as number_booked, 
                                workshop_attendance
                            FROM workshop l
                            JOIN 
                                workshop_info li ON l.workshop_title_id = li.workshop_info_id
                            JOIN 
                                location loc ON l.workshop_location = loc.location_id order by workshop_date asc;""")
        workshop = cursor.fetchall()
        return render_template('manage_attendance.html', filter="workshop", workshop=workshop)
    

@app.route("/viewlessonattendance/<int:lesson_id>", methods=["GET"])
@logged_in
def viewlessonattendance(lesson_id):
    #function will return all the booking made for this lesson
    cursor, connection = getCursor()
    cursor.execute("""select booking_id, lesson_date, TIME_FORMAT(lesson_start_time, '%h:%i %p') AS formatted_start_time, b.member_title, b.member_firstname, 
                   b.member_familyname, member_position, member_email, member_address, member_dob, booking_attended
                   from booking a, member b, lesson d
                   where a.booking_member_id = b.member_id and a.booking_lesson_id = d.lesson_id and 
                   booking_lesson_id = %s """, (lesson_id,))
    bookinglist = cursor.fetchall()

    cursor.execute("""select lesson_info_type, lesson_date, TIME_FORMAT(lesson_start_time, '%h:%i %p') AS formatted_start_time
                    from lesson a, lesson_info b
                    where a.lesson_title_id = b.lesson_info_id and lesson_id = %s """, (lesson_id,))
    lesson_info = cursor.fetchone()

    topic = lesson_info[0]
    date = lesson_info[1]
    date = date.strftime('%d-%m-%Y')
    starttime = lesson_info[2]
    type = "Lesson"

    cursor.close()
    connection.close()

    return render_template("manager_mark_attendance.html", bookinglist = bookinglist, lessonID = lesson_id, topic=topic, date=date, starttime=starttime, type=type)

@app.route("/viewworkshopattendance/<int:workshop_id>", methods=["GET"])
@logged_in
def viewworkshopattendance(workshop_id):
    #function will return all the booking made for this workshop
    cursor, connection = getCursor()
    cursor.execute("""select booking_id, workshop_date, TIME_FORMAT(workshop_time, '%h:%i %p') AS formatted_start_time, b.member_title, b.member_firstname, 
                   b.member_familyname, member_position, member_email, member_address, member_dob, booking_attended
                   from booking a, member b, workshop d
                   where a.booking_member_id = b.member_id and a.booking_workshop_id = d.workshop_id and 
                    booking_workshop_id = %s """, (workshop_id,))
    bookinglist = cursor.fetchall()

    cursor.execute("""select workshop_info_topic, workshop_date, TIME_FORMAT(workshop_time, '%h:%i %p') AS formatted_start_time
                    from workshop a, workshop_info b
                    where a.workshop_title_id = b.workshop_info_id and workshop_id = %s """, (workshop_id,))
    workshop_info = cursor.fetchone()

    topic = workshop_info[0]
    date = workshop_info[1]
    date = date.strftime('%d-%m-%Y')
    starttime = workshop_info[2]
    type = "Workshop"

    cursor.close()
    connection.close()

    return render_template("manager_mark_attendance.html", bookinglist = bookinglist, workshopID = workshop_id, topic=topic, date=date, starttime=starttime, type=type)



@app.route('/updateattendance', methods=['POST'])
@logged_in
def updateattendance():
    #function to update attendance 
    #booking ID retrieved from caller form
    #caller: manager_mark_attendance.html
    cursor, connection = getCursor()

    checked_values = request.form.getlist('checkbox')
    type = request.form.get('type')

    #loop through all the list of bookings to get the booking_id
    #check if the list is from workshop or lesson
    #update the attendance count respectively
    for value in checked_values:

        if value:
            booking_id = int(value)

            cursor.execute("""update booking set booking_attended = 1 where booking_id = %s;""",
                (booking_id,))

            if type == "Workshop":
                workshop_id = int(request.form.get('workshopID'))
                cursor.execute("""update workshop set workshop_attendance = CASE 
                                    WHEN workshop_attendance IS NULL THEN 1 
                                    ELSE workshop_attendance + 1 
                                END where workshop_id = %s;""",
                        (workshop_id,))               

            if type == "Lesson":
                lesson_id = int(request.form.get('lessonID'))
                cursor.execute("""update lesson set lesson_attendance = CASE 
                                    WHEN lesson_attendance IS NULL THEN 1 
                                    ELSE lesson_attendance + 1 
                                END where lesson_id = %s;""",
                        (lesson_id,))
            
    connection.commit()

    connection.close()
    flash(f'Attendance checked successfully', category='success')
    return redirect(url_for("trackattendance")) 
        
@app.route('/check_availability', methods=['POST'])
@logged_in
def check_availability():
    # Establish connection to the database
    cursor, connection = getCursor()
    request_data = request.get_json()
    workshop_date = request_data.get('workshopDate')
    start_time = request_data.get('startTime')
    # Execute the SQL query
    # Query will return all the tutors that is available within the timeslot selected
    sql_query = """
        SELECT CONCAT(staff_title, ' ', staff_firstname, ' ', staff_familyname) AS tutor_name
        FROM staff a, user b 
        WHERE a.staff_id = b.user_id 
        AND userrole = 'TT' 
        AND staff_id NOT IN (
            SELECT workshop_tutor_id 
            FROM workshop 
            WHERE workshop_date = %s 
            AND workshop_time BETWEEN %s AND ADDTIME(%s, '02:00:00')
        )
        AND staff_id NOT IN (
            SELECT lesson_tutor_id 
            FROM lesson 
            WHERE lesson_date = %s 
            AND lesson_start_time BETWEEN %s AND ADDTIME(%s, '01:00:00')
        )
    """
    cursor.execute(sql_query, (workshop_date, start_time, start_time, workshop_date, start_time, start_time))

    # Fetch the results
    available_tutors = cursor.fetchall()

    return jsonify(available_tutors)


# view the member Profile that booked the tutor lesson
@app.route('/subscriptionreportviewmember/<memberid>', methods=['GET'])
@logged_in
def subscriptionreportviewmember(memberid):

    viewonly=True
    form = EditMemberProfileForm()

    cursor, connection = getCursor()
    cursor.execute('SELECT * FROM member WHERE member_id = %s', (memberid,) )
    profile = cursor.fetchone()

    form.title.data = profile[1]
    form.firstname.data = profile[2]
    form.lastname.data = profile[3]
    membername = profile[2] + ' ' + profile[3]
    form.position.data = profile[4]
    form.phone.data = profile[5]
    form.email.data = profile[6]
    form.address.data = profile[7]
    form.dob.data = profile[8]

    #retrieve tutor image from image table
    cursor, connection = getCursor()
    cursor.execute('select * from image where user_id = %s', (memberid,))
    imagelist = cursor.fetchall()
    form.images.choices =  [(image[2]) for image in imagelist]

    closeConnection()
    return render_template("subscription_report_view_member.html", form=form, member_id=memberid, membername=membername)


@app.route("/viewlessonattendancepatterns/<int:lesson_id>", methods=["GET"])
@logged_in
def viewlessonattendancepatterns(lesson_id):
    #function will return all the attendance for this lesson
    cursor, connection = getCursor()
    cursor.execute("""select booking_id, lesson_date, TIME_FORMAT(lesson_start_time, '%h:%i %p') AS formatted_start_time, b.member_title, b.member_firstname, 
                   b.member_familyname, member_position, member_email, member_address, member_dob, lesson_booked
                   from booking a, member b, lesson d
                   where a.booking_member_id = b.member_id and a.booking_lesson_id = d.lesson_id and 
                   booking_lesson_id = %s """, (lesson_id,))
    bookinglist = cursor.fetchall()

    cursor.execute("""select lesson_info_type, lesson_date, TIME_FORMAT(lesson_start_time, '%h:%i %p') AS formatted_start_time
                    from lesson a, lesson_info b
                    where a.lesson_title_id = b.lesson_info_id and lesson_id = %s """, (lesson_id,))
    lesson_info = cursor.fetchone()

    topic = lesson_info[0]
    date = lesson_info[1]
    date = date.strftime('%d-%m-%Y')
    starttime = lesson_info[2]
    type = "Lesson"

    cursor.close()
    connection.close()

    return render_template("manager_patterns_members.html", bookinglist = bookinglist, lessonID = lesson_id, topic=topic, date=date, starttime=starttime, type=type)

@app.route("/viewworkshopattendancepatterns/<int:workshop_id>", methods=["GET"])
@logged_in
def viewworkshopattendancepatterns(workshop_id):
    #function will return all the attendance made for this workshop
    cursor, connection = getCursor()
    cursor.execute("""select booking_id, workshop_date, TIME_FORMAT(workshop_time, '%h:%i %p') AS formatted_start_time, b.member_title, b.member_firstname, 
                   b.member_familyname, member_position, member_email, member_address, member_dob, booking_attended
                   from booking a, member b, workshop d
                   where a.booking_member_id = b.member_id and a.booking_workshop_id = d.workshop_id and 
                   booking_attended > 0 and booking_workshop_id = %s """, (workshop_id,))
    bookinglist = cursor.fetchall()

    cursor.execute("""select workshop_info_topic, workshop_date, TIME_FORMAT(workshop_time, '%h:%i %p') AS formatted_start_time
                    from workshop a, workshop_info b
                    where a.workshop_title_id = b.workshop_info_id and workshop_id = %s """, (workshop_id,))
    workshop_info = cursor.fetchone()

    topic = workshop_info[0]
    date = workshop_info[1]
    date = date.strftime('%d-%m-%Y')
    starttime = workshop_info[2]
    type = "Workshop"

    cursor.close()
    connection.close()

    return render_template("manager_patterns_members.html", bookinglist = bookinglist, workshopID = workshop_id, topic=topic, date=date, starttime=starttime, type=type)


