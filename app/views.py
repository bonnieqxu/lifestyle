from app import app
from flask import render_template, request
import mysql.connector
import app.connect as connect


dbconn = None
connection = None

def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
    password=connect.dbpass, host=connect.dbhost, auth_plugin='mysql_native_password',\
    database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn


@app.route("/")
def landingpage():
    return render_template("landing_page.html")


@app.route("/view_workshop", methods=['GET', 'POST'])
def view_workshop():
    # sort_by = request.args.get('sort_by', default='workshop_date')
    if request.method == 'GET':       
        # If it's a GET request, simply retrieve all workshops
        connection =  getCursor()

        sql = """
            SELECT 
                w.workshop_id AS workshop_id,
                CONCAT(s.staff_title, ' ', s.staff_firstname, ' ', s.staff_familyname) AS tutor,
                wi.workshop_info_topic AS workshop_topic,
                w.workshop_detail AS workshop_detail,
                w.workshop_date AS workshop_date,
                w.workshop_time AS workshop_time,
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
                """

        #     ORDER BY {};
        # """.format(sort_by)       

        connection.execute(sql)
        workshop_timetable = connection.fetchall()
        return render_template('workshop_timetable.html', workshop_timetable=workshop_timetable)


@app.route('/view_tutor_list_for_visitor', methods=['GET'])
def view_tutor_list_for_visitor():

        
    if request.method == 'GET':
        # If it's a GET request, simply retrieve all workshops
        connection = getCursor()
            # SQL query to retrieve staff information for users with role 'TT' including images
        sql = """
            SELECT s.staff_id, s.staff_title, s.staff_firstname, s.staff_familyname, 
                    s.staff_position, s.staff_phonenumber, s.staff_email, s.staff_profile, 
                    i.image
            FROM staff s
            JOIN user u ON s.staff_id = u.user_id
            LEFT JOIN image i ON s.staff_id = i.user_id
            WHERE u.userrole = 'TT';
             """
        connection.execute(sql)
        tutor_list = connection.fetchall()
        connection.close()  # Close the connection
            
            # Render the provided template with retrieved data
        return render_template("view_tutor_list_for_visitor.html", tutor_list=tutor_list)        


@app.route('/view_tutor_details_for_visitor/<int:tutor_id>', methods=['GET'])
def view_tutor_details_for_visitor(tutor_id):
    if request.method == 'GET':
        connection = getCursor()
        # SQL query to retrieve details of the selected tutor
        sql = """
            SELECT s.staff_id, s.staff_title, s.staff_firstname, s.staff_familyname, 
                    s.staff_position, s.staff_phonenumber, s.staff_email, s.staff_profile, 
                    i.image
            FROM staff s
            LEFT JOIN image i ON s.staff_id = i.user_id
            WHERE s.staff_id = %s;
             """
        connection.execute(sql, (tutor_id,))
        tutor_details = connection.fetchone()
        connection.close()  # Close the connection
        
 
            # Render the provided template with retrieved data
        return render_template("view_tutor_details_for_visitor.html", tutor_details=tutor_details)
