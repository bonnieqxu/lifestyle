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

# tutor dashboard
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

    #Fetch users full name to be used in the welcome message
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

    #viewonly parameter set to True for readonly
    #reuse of member_views.html
    viewonly=True
    form = EditMemberProfileForm()

    # Get cursor and connection
    cursor, connection = getCursor()

    # Retrieve member details from the database
    cursor.execute('SELECT * FROM member WHERE member_id = %s', (memberid,) )
    profile = cursor.fetchone()

    # Populate form fields with member details
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
    #function will return all lessons which belongs to the current tutor
    cursor, connection = getCursor()
    cursor.execute("""select lesson_id, lesson_title_id, lesson_date, TIME_FORMAT(lesson_start_time, '%h:%i %p') AS lesson_start_time , location_name, location_description, 
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
    #function will return all the lessons booked which belongs to the current tutor
    cursor, connection = getCursor()
    cursor.execute("""select booking_member_id, lesson_date, TIME_FORMAT(lesson_start_time, '%h:%i %p') AS lesson_start_time, b.member_title, b.member_firstname, 
                   b.member_familyname, e.location_name, lesson_info_type, lesson_detail
                   from booking a, member b, lesson_info c, lesson d, location e
                   where a.booking_member_id = b.member_id and d.lesson_title_id = c. lesson_info_id 
                   and a.booking_lesson_id = d.lesson_id and d.lesson_location = e.location_id and
                    d.lesson_booked=true and lesson_date > curdate() and booking_staff_id = %s 
                   order by lesson_date asc """, (session['id'],))
    tutorlessonbookinglist = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template("tutor_lesson_booking_list.html", tutorlessonbookinglist = tutorlessonbookinglist)

@app.route('/marktutorlessonattendancelist')
@logged_in
def marktutorlessonattendancelist():
    #function will return all booked lessons for the tutor to mark attendance
    cursor, connection = getCursor()
    cursor.execute("""select booking_id,  lesson_date, TIME_FORMAT(lesson_start_time, '%h:%i %p') AS lesson_start_time, b.member_title, b.member_firstname, 
                   b.member_familyname, e.location_name, lesson_info_type, lesson_detail, lesson_id,  (select count(*)  from booking where booking_lesson_id = lesson_id) as number_booked,lesson_attendance
                   from booking a, member b, lesson_info c, lesson d, location e
                   where a.booking_member_id = b.member_id and d.lesson_title_id = c.lesson_info_id 
                   and a.booking_lesson_id = d.lesson_id and d.lesson_location = e.location_id and
                   d.lesson_booked=true 
                   and booking_staff_id = %s 
                   order by lesson_date asc """, (session['id'],))
    tutorlessonbookinglist = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template("tutor_lesson_attendance.html", tutorlessonbookinglist = tutorlessonbookinglist)

@app.route('/marktutorworkshopattendancelist')
@logged_in
def marktutorworkshopattendancelist():
    #function will return all booked lessons for the tutor to mark attendance
    cursor, connection = getCursor()
    cursor.execute("""select workshop_date, TIME_FORMAT(workshop_time, '%h:%i %p') AS workshop_time, e.location_name, e.location_description, 
                   workshop_info_topic, workshop_detail, workshop_id, (select count(*)  from booking where booking_workshop_id = d.workshop_id) as number_booked, workshop_attendance
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
    #function will return all the members who booked the workshop
    cursor, connection = getCursor()
    # Retrieve member workshop booking details from the database
    cursor.execute("""select booking_id,  b.member_title, b.member_firstname, b.member_familyname, b.member_position,
                   b.member_phonenumber, b.member_email, b.member_address, b.member_dob, 
	                b. member_id, workshop_id, workshop_attendance, booking_attended
                   from booking a, member b, workshop_info c, workshop d, location e
                   where a.booking_member_id = b.member_id and d.workshop_title_id = c. workshop_info_id 
                   and a.booking_workshop_id = d.workshop_id and d.workshop_location = e.location_id 
                   and workshop_id = %s """, (workshop_id,))
    memberworkshopbookinglist = cursor.fetchall()

    # Retrieve workshop information
    cursor.execute("""select workshop_info_topic, workshop_date, TIME_FORMAT(workshop_time, '%h:%i %p') AS formatted_start_time
                    from workshop a, workshop_info b
                    where a.workshop_title_id = b.workshop_info_id and workshop_id = %s """, (workshop_id,))
    workshop_info = cursor.fetchone()

    topic = workshop_info[0]
    date = workshop_info[1]
    date = date.strftime('%d-%m-%Y')
    starttime = workshop_info[2]

    cursor.close()
    connection.close()

    return render_template("tutor_member_workshop_list.html", memberworkshopbookinglist = memberworkshopbookinglist, workshopID = workshop_id, topic=topic, date=date, starttime=starttime)


@app.route('/updateworkshopattendance', methods=['POST'])
@logged_in
def updateworkshopattendance():
    #function to update workshop attendance
    #workshop ID retrieved from caller form
    #caller: tutor_member_workshop_list.html
    cursor, connection = getCursor()

    # Get list of checked checkboxes and workshop ID from the form
    checked_values = request.form.getlist('checkbox')
    workshop_id = int(request.form.get('workshopID'))

    #loop through all the checked checkboxes to get the booking ID
    for value in checked_values:

        if value:
            booking_id = int(value)

            # Update booking_attended status for the selected booking
            cursor.execute("""update booking set booking_attended = 1 where booking_id = %s;""",
                    (booking_id,))
            
            # Update workshop attendance count
            cursor.execute("""update workshop set workshop_attendance = CASE 
                                WHEN workshop_attendance IS NULL THEN 1 
                                ELSE workshop_attendance + 1 
                            END where workshop_id = %s;""",
                    (workshop_id,))
            
            connection.commit()

    # Flash message for successful workshop attendance update
    flash(f'Workshop attendance checked successfully', category='success')

    connection.close()
    return redirect("/marktutorworkshopattendancelist")


@app.route('/updatelessonattendance', methods=['POST'])
@logged_in
def updatelessonattendance():
    #function to update lesson attendance
    #member ID retrieved from caller form
    #caller: tutor_lesson_attendance.html
    cursor, connection = getCursor()

    # Get booking ID and lesson ID from the form
    booking_id = int(request.form.get('bookingID'))
    lesson_id = int(request.form.get('lessonID'))

    # Update booking attendance status for the selected booking
    cursor.execute("""update booking set booking_attended = 1 where booking_id = %s;""",
            (booking_id,))
    
    # Update lesson attendance status for the selected lesson
    cursor.execute("""update lesson set lesson_attendance = '1' where lesson_id = %s;""",
            (lesson_id,))
    
    connection.commit()
    
    # Flash message for successful lesson attendance update
    flash(f'Lesson attendance checked successfully', category='success')

    connection.close()
    return redirect("/marktutorlessonattendancelist")


# Profile route
@app.route('/tutor/profile', methods=['GET', 'POST'])
@logged_in
def tutor_profile():
    #function to retrieve tutor profile for editing
    tutorid = session['id']
    # Fetch the user's profile information from the database
    msg=''
    form=EditTutorProfileForm()

    if request.method == 'GET':
        # Retrieve profile information for the tutor
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
        # Update tutor profile with new information
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
    #function to allow tutor to create lesson
    form = AddTutorLessonForm()

    cursor, connection = getCursor()

    # Fetch lesson titles and locations from MySQL
    cursor.execute("SELECT lesson_info_id, lesson_info_type FROM lesson_info;")
    titles = cursor.fetchall()

    cursor.execute("SELECT location_id, location_name FROM location;")
    locations = cursor.fetchall()

    # Populate choices for lesson titles and locations in the form
    form.title.choices = titles
    form.location.choices = locations

    # Retrieve lesson information from the database for displaying in the form
    cursor.execute("SELECT lesson_info_id, lesson_info_type, lesson_info_desc FROM lesson_info;")
    titles = cursor.fetchall()
    # Convert the titles data to a list of dictionaries
    titles_data = [{'id': title[0], 'type': title[1], 'desc': title[2]} for title in titles]

    cursor.close()
    connection.close()

    return render_template('add_tutor_lesson.html', form=form, titles_data=titles_data)


@app.route('/inserttutorlesson', methods=['POST'])
@logged_in
def inserttutorlesson():
    #function to insert a new lesson 
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
        # Retrieve form data
        lessontitle = form.title.data
        lessonlocation = form.location.data
        lessondate = form.lessondate.data
        lessonstarttime = form.lessonstarttime.data
        lessondesc = form.lessondesc.data

        cursor, connection = getCursor()

        # Check for timetable clashes with existing workshops or lessons
        cursor.execute('select * from workshop where workshop_tutor_id = %s and workshop_date = %s and workshop_time=%s',
                            ( session['id'], lessondate, lessonstarttime, ))
        workshop_clash = cursor.fetchone()

        cursor.execute('select * from lesson where lesson_tutor_id = %s and lesson_date = %s and lesson_start_time = %s',
                    ( session['id'], lessondate, lessonstarttime, ))
        lesson_clash = cursor.fetchone()

        #section below checks if there is existing workshop or lesson that clashes with the new lesson
        if workshop_clash is None and lesson_clash is None:
            # Insert new lesson into the database
            cursor.execute('INSERT INTO lesson (lesson_title_id, lesson_tutor_id, lesson_location, lesson_date, lesson_start_time, lesson_detail ) VALUES ( %s, %s, %s, %s, %s, %s)',
                            (lessontitle, session['id'], lessonlocation, lessondate, lessonstarttime, lessondesc, ))
            connection.commit()

            # Show success message and redirect to lesson list
            flash(f'Lesson created successfully', category='success')

            connection.close()
            return redirect(url_for('viewtutorlessonlist'))
        else: 
            # Show error message if there are timetable clashes
            msg = "Failed to create lesson due to timetable clash"
            return render_template('add_tutor_lesson.html', title='Add New Lesson', form=form, msg=msg)
    elif request.method == 'POST':
        # Form submission failed, show error message
        msg = 'Please fill out the form!'
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

    # Populate choices for lesson titles and locations in the form
    form.title.choices = titles
    form.location.choices = locations

    # Retrieve lesson details from the database
    cursor.execute('SELECT * FROM lesson WHERE lesson_id = %s', (lessonid,) )
    lessonList = cursor.fetchall()

    # Populate form fields with lesson details
    form.title.data = lessonList[0][1]
    form.location.data = lessonList[0][3]
    form.lessondate.data = lessonList[0][4]
    form.lessondesc.data = lessonList[0][7]

    # Convert lesson start time to time object
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
    #function to update a tutor lessson
    msg=''
    form=EditTutorLessonForm()

    cursor, connection = getCursor()

    # Fetch titles from MySQL
    cursor.execute("SELECT lesson_info_id, lesson_info_type FROM lesson_info;")
    titles = cursor.fetchall()

    cursor.execute("SELECT location_id, location_name FROM location;")
    locations = cursor.fetchall()

    # Populate choices for lesson titles and locations in the form
    form.title.choices = titles
    form.location.choices = locations

    if form.validate_on_submit():
        # Retrieve form data
        lesson_id = request.form.get('lesson_id')
        title = form.title.data
        location = form.location.data
        lessondate = form.lessondate.data
        lessonstarttime = form.lessonstarttime.data
        lessondesc = form.lessondesc.data

        # Check for timetable clashes with existing workshops or lessons
        cursor.execute("""select * from workshop where workshop_tutor_id = %s 
                            and workshop_date = %s and workshop_time=%s""",
                            ( session['id'], lessondate, lessonstarttime, ))
        workshop_clash = cursor.fetchone()

        cursor.execute("""select * from lesson where lesson_tutor_id = %s 
                            and lesson_date = %s and lesson_start_time = %s and lesson_id <> %s""",
                    ( session['id'], lessondate, lessonstarttime, lesson_id, ))
        lesson_clash = cursor.fetchone()

        # Check if there are clashes; if not, update the lesson
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
    # If form submission is not valid, return error message
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    connection.close()
    return render_template('edit_tutor_lesson.html', title='Edit Lesson', form=form, msg=msg)


@app.route('/deletetutorlesson', methods=['POST'])
@logged_in
def deletetutorlesson():
    #function to delete tutor lesson
    #lesson ID retrieved from caller form
    #caller: tutor_lesson_list.html
    cursor, connection = getCursor()

    # Get the lesson ID from the form data
    lesson_id = int(request.form.get('lessonID'))

    # Delete the lesson from the database
    cursor.execute("""delete from lesson where lesson_id = %s;""",
            (lesson_id,))
    
    connection.commit()
    connection.close()
    
    # Flash success message
    flash(f'Lesson deleted successfully', category='success')

    return redirect("/viewtutorlessonlist")


# view workshop schedule
@app.route("/tutor_view_workshop", methods=['GET', 'POST'])
@logged_in
def tutor_view_workshop():
    cursor, connection = getCursor()

    # Get the ID of the logged-in tutor from the session
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
                    TIME_FORMAT(w.workshop_time, '%h:%i %p') AS workshop_time,
                    l.location_name,
                    l.location_description AS workshop_location,
                    w.workshop_cost AS workshop_cost,
                    w.workshop_cap_limit AS workshop_cap_limit,
                    l.location_map
                FROM 
                    workshop w
                INNER JOIN 
                    staff s ON w.workshop_tutor_id = s.staff_id
                INNER JOIN 
                    workshop_info wi ON w.workshop_title_id = wi.workshop_info_id
                INNER JOIN 
                    location l ON w.workshop_location = l.location_id
                WHERE 
                    w.workshop_date >= curdate() and
                    w.workshop_tutor_id = %s
                    order by w.workshop_date asc
            """
            cursor.execute(sql, (tutor_id,))
        workshops = cursor.fetchall()
        connection.close()  # Close connection after use

        return render_template("tutor_workshop.html", workshops=workshops)
    else:
        # if "clear filter"
        if 'clear_filter' in request.args:
        # view full list
            sql = """
                SELECT 
                    w.workshop_id AS workshop_id,
                    CONCAT(s.staff_title, ' ', s.staff_firstname, ' ', s.staff_familyname) AS tutor,
                    wi.workshop_info_topic AS workshop_topic,
                    wi.workshop_info_desc AS workshop_detail,
                    w.workshop_date AS workshop_date,
                    TIME_FORMAT(w.workshop_time, '%h:%i %p') AS workshop_time,
                    l.location_name,
                    l.location_description AS workshop_location,
                    w.workshop_cost AS workshop_cost,
                    w.workshop_cap_limit AS workshop_cap_limit,
                    l.location_map
                FROM 
                    workshop w
                INNER JOIN 
                    staff s ON w.workshop_tutor_id = s.staff_id
                INNER JOIN 
                    workshop_info wi ON w.workshop_title_id = wi.workshop_info_id
                INNER JOIN 
                    location l ON w.workshop_location = l.location_id
                WHERE w.workshop_date >= curdate()
                order by w.workshop_date asc;
            """
        else:
            sql = """
                SELECT 
                    w.workshop_id AS workshop_id,
                    CONCAT(s.staff_title, ' ', s.staff_firstname, ' ', s.staff_familyname) AS tutor,
                    wi.workshop_info_topic AS workshop_topic,
                    wi.workshop_info_desc AS workshop_detail,
                    w.workshop_date AS workshop_date,
                    TIME_FORMAT(w.workshop_time, '%h:%i %p') AS workshop_time,
                    l.location_name,
                    l.location_description AS workshop_location,
                    w.workshop_cost AS workshop_cost,
                    w.workshop_cap_limit AS workshop_cap_limit,
                    l.location_map
                FROM 
                    workshop w
                INNER JOIN 
                    staff s ON w.workshop_tutor_id = s.staff_id
                INNER JOIN 
                    workshop_info wi ON w.workshop_title_id = wi.workshop_info_id
                INNER JOIN 
                    location l ON w.workshop_location = l.location_id
                WHERE 
                    w.workshop_date >= curdate()
                order by w.workshop_date asc;
            """
        cursor.execute(sql)
        workshops = cursor.fetchall()

        connection.close()  # Close connection after use
        # Pass the workshops to the template along with the existing context
        return render_template("tutor_workshop.html", workshops=workshops)