from app import app
from flask import render_template, session, redirect, url_for, request, flash, jsonify
import mysql.connector
import app.connect as connect
from app.utility import logged_in
from datetime import datetime, timedelta
from app.forms import EditTutorForm, AddTutorLessonForm, EditTutorLessonForm, EditTutorProfileForm, EditMemberProfileForm
import os, uuid  # For generating unique identifiers
import json
from datetime import time

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

@app.route('/tutor_home')
@logged_in
def tutor_home():

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
    return render_template('tutor_home.html', user_id=user_id, image=image, userfullname=userfullname)


# view the member Profile that booked the tutor lesson
@app.route('/viewtutormemberprofile/<memberid>', methods=['GET'])
@logged_in
def viewtutormemberprofile(memberid):

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
    return render_template("member_views.html", form=form, member_id=memberid, membername=membername, view=viewonly)
    

@app.route('/viewtutorlessonlist')
@logged_in
def viewtutorlessonlist():
    #function will return all the workshop type
    cursor, connection = getCursor()
    cursor.execute("""select lesson_id, lesson_title_id, lesson_date, lesson_start_time, location_name, location_description, 
                    lesson_info_type, lesson_detail from lesson a, lesson_info b, location c where a.lesson_title_id = b.lesson_info_id 
                   and a.lesson_location = c.location_id and lesson_tutor_id = %s and a.lesson_booked = false
                   order by lesson_date, lesson_start_time asc """, (session['id'],))
    tutorlessonlist = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template("tutor_lesson_list.html", tutorlessonlist = tutorlessonlist)


@app.route('/viewtutorlessonbookinglist')
@logged_in
def viewtutorlessonbookinglist():
    #function will return all the workshop type
    cursor, connection = getCursor()
    cursor.execute("""select booking_member_id, lesson_date, lesson_start_time, b.member_title, b.member_firstname, 
                   b.member_familyname, e.location_name, lesson_info_type, lesson_detail
                   from booking a, member b, lesson_info c, lesson d, location e
                   where a.booking_member_id = b.member_id and d.lesson_title_id = c. lesson_info_id 
                   and a.booking_lesson_id = d.lesson_id and d.lesson_location = e.location_id and
                    d.lesson_booked=true and booking_staff_id = %s 
                   order by lesson_date asc """, (session['id'],))
    tutorlessonbookinglist = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template("tutor_lesson_booking_list.html", tutorlessonbookinglist = tutorlessonbookinglist)

@app.route('/marktutorlessonattendancelist')
@logged_in
def marktutorlessonattendancelist():
    #function will return all the workshop type
    cursor, connection = getCursor()
    cursor.execute("""select booking_id,  lesson_date, lesson_start_time, b.member_title, b.member_firstname, 
                   b.member_familyname, e.location_name, lesson_info_type, lesson_detail, lesson_id
                   from booking a, member b, lesson_info c, lesson d, location e
                   where a.booking_member_id = b.member_id and d.lesson_title_id = c.lesson_info_id 
                   and a.booking_lesson_id = d.lesson_id and d.lesson_location = e.location_id and
                   d.lesson_booked=true 
                   and lesson_attendance is null and booking_staff_id = %s 
                   order by lesson_date asc """, (session['id'],))
    tutorlessonbookinglist = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template("tutor_lesson_attendance.html", tutorlessonbookinglist = tutorlessonbookinglist)

@app.route('/marktutorworkshopattendancelist')
@logged_in
def marktutorworkshopattendancelist():
    #function will return all the workshop type
    cursor, connection = getCursor()
    cursor.execute("""select workshop_date, workshop_time, e.location_name, e.location_description, 
                   workshop_info_topic, workshop_detail, workshop_id, workshop_attendance
                   from workshop_info c, workshop d, location e
                   where c.workshop_info_id = d.workshop_title_id
                   and d.workshop_location = e.location_id and workshop_tutor_id = %s 
                   order by workshop_date asc """, (session['id'],))
    tutorworkshopbookinglist = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template("tutor_workshop_attendance.html", tutorworkshopbookinglist = tutorworkshopbookinglist)

@app.route('/viewmemberworkshop/<int:workshop_id>', methods=['GET'])
@logged_in
def viewmemberworkshop(workshop_id):
    #function will return all the workshop type
    cursor, connection = getCursor()
    cursor.execute("""select booking_id,  b.member_title, b.member_firstname, b.member_familyname, b.member_position,
                   b.member_phonenumber, b.member_email, b.member_address, b.member_dob, 
	                b. member_id, workshop_id, workshop_attendance
                   from booking a, member b, workshop_info c, workshop d, location e
                   where a.booking_member_id = b.member_id and d.workshop_title_id = c. workshop_info_id 
                   and (a.booking_attended = 0 or booking_attended is null) and a.booking_workshop_id = d.workshop_id and d.workshop_location = e.location_id 
                   and workshop_id = %s """, (workshop_id,))
    memberworkshopbookinglist = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template("tutor_member_workshop_list.html", memberworkshopbookinglist = memberworkshopbookinglist)


@app.route('/updateworkshopattendance', methods=['POST'])
@logged_in
def updateworkshopattendance():
    #function to delete member
    #member ID retrieved from caller form
    #caller: memberlist.html
    cursor, connection = getCursor()

    booking_id = int(request.form.get('bookingID'))
    workshop_id = int(request.form.get('workshopID'))

    cursor.execute("""update booking set booking_attended = 1 where booking_id = %s;""",
            (booking_id,))
    
    cursor.execute("""update workshop set workshop_attendance = CASE 
                          WHEN workshop_attendance IS NULL THEN 1 
                          ELSE workshop_attendance + 1 
                      END where workshop_id = %s;""",
            (workshop_id,))
    
    connection.commit()
    
    flash(f'Workshop attendance checked successfully', category='success')

    connection.close()
    return redirect("/marktutorworkshopattendancelist")


@app.route('/updatelessonattendance', methods=['POST'])
@logged_in
def updatelessonattendance():
    #function to delete member
    #member ID retrieved from caller form
    #caller: memberlist.html
    cursor, connection = getCursor()

    booking_id = int(request.form.get('bookingID'))
    lesson_id = int(request.form.get('lessonID'))

    cursor.execute("""update booking set booking_attended = 1 where booking_id = %s;""",
            (booking_id,))
    
    cursor.execute("""update lesson set lesson_attendance = '1' where lesson_id = %s;""",
            (lesson_id,))
    
    connection.commit()
    
    flash(f'Lesson attendance checked successfully', category='success')

    connection.close()
    return redirect("/marktutorlessonattendancelist")

# Profile route
@app.route('/tutor/profile', methods=['GET', 'POST'])
@logged_in
def tutor_profile():

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

        #retrieve tutor image from image table
        cursor, connection = getCursor()
        cursor.execute('select * from image where user_id = %s', (tutorid,))
        imagelist = cursor.fetchall()
        form.images.choices =  [(image[2]) for image in imagelist]

        closeConnection()
        return render_template("tutor_views.html", form=form, tutor_id = tutorid, tutorname = tutorname)

  
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
        return redirect(url_for('tutor_profile'))
    closeConnection()
    return render_template('tutor_views.html', title='Edit Tutor', form=form, msg=msg)
    

@app.route('/addtutorlesson')
@logged_in
def addtutorlesson():
    form = AddTutorLessonForm()

    cursor, connection = getCursor()

    # Fetch titles from MySQL
    cursor.execute("SELECT lesson_info_id, lesson_info_type FROM lesson_info;")
    titles = cursor.fetchall()

    cursor.execute("SELECT location_id, location_name FROM location;")
    locations = cursor.fetchall()

    form.title.choices = titles
    form.location.choices = locations

    cursor.execute("SELECT lesson_info_id, lesson_info_type, lesson_info_desc FROM lesson_info;")
    titles = cursor.fetchall()
    # Convert the titles data to a list of dictionaries
    titles_data = [{'id': title[0], 'type': title[1], 'desc': title[2]} for title in titles]

    # Create form and populate choices
    cursor.close()
    connection.close()

    return render_template('add_tutor_lesson.html', form=form, titles_data=titles_data)

@app.route('/inserttutorlesson', methods=['POST'])
@logged_in
def inserttutorlesson():
    #function to create a lesson
    msg=''
    form=AddTutorLessonForm()

    cursor, connection = getCursor()

    # Fetch titles from MySQL
    cursor.execute("SELECT lesson_info_id, lesson_info_type FROM lesson_info;")
    titles = cursor.fetchall()

    cursor.execute("SELECT location_id, location_name FROM location;")
    locations = cursor.fetchall()

    # Close cursor and connection
    cursor.close()
    connection.close()

    # Create form and populate choices
    form.title.choices = titles
    form.location.choices = locations

    if form.validate_on_submit():
        lessontitle = form.title.data
        lessonlocation = form.location.data
        lessondate = form.lessondate.data
        lessonstarttime = form.lessonstarttime.data
        lessondesc = form.lessondesc.data

        cursor, connection = getCursor()

        cursor.execute('select * from workshop where workshop_tutor_id = %s and workshop_date = %s and workshop_time=%s',
                            ( session['id'], lessondate, lessonstarttime, ))
        workshop_clash = cursor.fetchone()

        cursor.execute('select * from lesson where lesson_tutor_id = %s and lesson_date = %s and lesson_start_time = %s',
                    ( session['id'], lessondate, lessonstarttime, ))
        lesson_clash = cursor.fetchone()

        if workshop_clash is None and lesson_clash is None:
            cursor.execute('INSERT INTO lesson (lesson_title_id, lesson_tutor_id, lesson_location, lesson_date, lesson_start_time, lesson_detail ) VALUES ( %s, %s, %s, %s, %s, %s)',
                            (lessontitle, session['id'], lessonlocation, lessondate, lessonstarttime, lessondesc, ))
            connection.commit()

            flash(f'Lesson created successfully', category='success')
            #once registration is successful, user will be routed to the login screen
            connection.close()
            return redirect(url_for('viewtutorlessonlist'))
        else: 
            msg = "Failed to create lesson due to timetable clash"
            return render_template('add_tutor_lesson.html', title='Add New Lesson', form=form, msg=msg)
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    connection.close()
    return render_template('add_tutor_lesson.html', title='Add New Lesson', form=form, msg=msg)

@app.route("/edittutorlesson/<lessonid>", methods=["GET"])
@logged_in
def edittutorlesson(lessonid):
    #function to retrieve tutor lesson for editing
    #lesson ID passed in via hyperlink
    #caller: tutor_lesson_list.html
    form=EditTutorLessonForm()

    cursor, connection = getCursor()

    # Fetch titles from MySQL
    cursor.execute("SELECT lesson_info_id, lesson_info_type FROM lesson_info;")
    titles = cursor.fetchall()

    cursor.execute("SELECT location_id, location_name FROM location;")
    locations = cursor.fetchall()

    form.title.choices = titles
    form.location.choices = locations

    cursor.execute('SELECT * FROM lesson WHERE lesson_id = %s', (lessonid,) )
    lessonList = cursor.fetchall()
    form.title.data = lessonList[0][1]
    form.location.data = lessonList[0][3]
    form.lessondate.data = lessonList[0][4]
    form.lessondesc.data = lessonList[0][7]

    if lessonList[0][5] is None:
        start_time = time(0, 0)  # Assign a default time, e.g., midnight
    else:
        start_time = time.fromisoformat(str(lessonList[0][5]))
    form.lessonstarttime.data = start_time

    connection.close()
    return render_template("edit_tutor_lesson.html", form=form, lesson_id = lessonid)


@app.route('/updatetutorlesson', methods=['POST'])
@logged_in
def updatetutorlesson():
    #function to edit guide
    msg=''
    form=EditTutorLessonForm()

    cursor, connection = getCursor()

    # Fetch titles from MySQL
    cursor.execute("SELECT lesson_info_id, lesson_info_type FROM lesson_info;")
    titles = cursor.fetchall()

    cursor.execute("SELECT location_id, location_name FROM location;")
    locations = cursor.fetchall()

    form.title.choices = titles
    form.location.choices = locations

    if form.validate_on_submit():

        lesson_id = request.form.get('lesson_id')
        title = form.title.data
        location = form.location.data
        lessondate = form.lessondate.data
        lessonstarttime = form.lessonstarttime.data
        lessondesc = form.lessondesc.data

        cursor.execute("""select * from workshop where workshop_tutor_id = %s 
                            and workshop_date = %s and workshop_time=%s""",
                            ( session['id'], lessondate, lessonstarttime, ))
        workshop_clash = cursor.fetchone()

        cursor.execute("""select * from lesson where lesson_tutor_id = %s 
                            and lesson_date = %s and lesson_start_time = %s and lesson_id <> %s""",
                    ( session['id'], lessondate, lessonstarttime, lesson_id, ))
        lesson_clash = cursor.fetchone()

        if workshop_clash is None and lesson_clash is None:

            cursor.execute("""UPDATE lesson SET lesson_title_id=%s, lesson_location= %s, 
                        lesson_date =%s, lesson_start_time =%s, lesson_detail=%s
                        WHERE lesson_id = %s;""",
                                ( title, location, lessondate, lessonstarttime, lessondesc, lesson_id, ))

            flash('Lesson updated successfully', category='success')
            connection.close()
            return redirect("/viewtutorlessonlist")
        else: 
            msg = "Failed to edit lesson due to timetable clash"
            return render_template('edit_tutor_lesson.html', title='Edit Lesson', form=form, msg=msg)
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    connection.close()
    return render_template('edit_tutor_lesson.html', title='Edit Lesson', form=form, msg=msg)


@app.route('/deletetutorlesson', methods=['POST'])
@logged_in
def deletetutorlesson():
    #function to delete tutor lesson
    #lesson ID retrieved from caller form
    #caller: totor_lesson_list.html
    cursor, connection = getCursor()

    lesson_id = int(request.form.get('lessonID'))

    cursor.execute("""delete from lesson where lesson_id = %s;""",
            (lesson_id,))
    
    connection.commit()
    connection.close()
    
    flash(f'Lesson deleted successfully', category='success')

    return redirect("/viewtutorlessonlist")




# view workshop schedule
@app.route("/tutor_view_workshop", methods=['GET', 'POST'])
@logged_in
def tutor_view_workshop():
    cursor, connection = getCursor()

    tutor_id = session.get('id')

    if request.method == 'POST':
        only_my_workshops = request.form.get('only_my_workshops')
        # if applies filter
        if only_my_workshops:
            sql = """
                SELECT 
                    w.workshop_id AS workshop_id,
                    CONCAT(s.staff_title, ' ', s.staff_firstname, ' ', s.staff_familyname) AS tutor,
                    wi.workshop_info_topic AS workshop_topic,
                    wi.workshop_info_desc AS workshop_detail,
                    w.workshop_date AS workshop_date,
                    w.workshop_time AS workshop_time,
                    l.location_name AS workshop_location,
                    w.workshop_cost AS workshop_cost,
                    w.workshop_cap_limit AS workshop_cap_limit
                FROM 
                    workshop w
                INNER JOIN 
                    staff s ON w.workshop_tutor_id = s.staff_id
                INNER JOIN 
                    workshop_info wi ON w.workshop_title_id = wi.workshop_info_id
                INNER JOIN 
                    location l ON w.workshop_location = l.location_id
                WHERE 
                    w.workshop_tutor_id = %s
            """
            cursor.execute(sql, (tutor_id,))
        workshops = cursor.fetchall()
        connection.close()  # Close connection after use

        return render_template("tutor_workshop.html", workshops=workshops)
    else:
        # if "clear filter"
        if 'clear_filter' in request.args:
        # if view full list
            sql = """
                SELECT 
                    w.workshop_id AS workshop_id,
                    CONCAT(s.staff_title, ' ', s.staff_firstname, ' ', s.staff_familyname) AS tutor,
                    wi.workshop_info_topic AS workshop_topic,
                    wi.workshop_info_desc AS workshop_detail,
                    w.workshop_date AS workshop_date,
                    w.workshop_time AS workshop_time,
                    l.location_name AS workshop_location,
                    w.workshop_cost AS workshop_cost,
                    w.workshop_cap_limit AS workshop_cap_limit
                FROM 
                    workshop w
                INNER JOIN 
                    staff s ON w.workshop_tutor_id = s.staff_id
                INNER JOIN 
                    workshop_info wi ON w.workshop_title_id = wi.workshop_info_id
                INNER JOIN 
                    location l ON w.workshop_location = l.location_id;
            """
        else:
            sql = """
                SELECT 
                    w.workshop_id AS workshop_id,
                    CONCAT(s.staff_title, ' ', s.staff_firstname, ' ', s.staff_familyname) AS tutor,
                    wi.workshop_info_topic AS workshop_topic,
                    wi.workshop_info_desc AS workshop_detail,
                    w.workshop_date AS workshop_date,
                    w.workshop_time AS workshop_time,
                    l.location_name AS workshop_location,
                    w.workshop_cost AS workshop_cost,
                    w.workshop_cap_limit AS workshop_cap_limit
                FROM 
                    workshop w
                INNER JOIN 
                    staff s ON w.workshop_tutor_id = s.staff_id
                INNER JOIN 
                    workshop_info wi ON w.workshop_title_id = wi.workshop_info_id
                INNER JOIN 
                    location l ON w.workshop_location = l.location_id;
            """
        cursor.execute(sql)
        workshops = cursor.fetchall()

        connection.close()  # Close connection after use
        # Pass the workshops to the template along with the existing context
        return render_template("tutor_workshop.html", workshops=workshops)