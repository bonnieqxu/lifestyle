from app import app
from flask import render_template, session, redirect, url_for, request, flash
import mysql.connector
import app.connect as connect
from flask_hashing import Hashing
from app.utility import logged_in

# Create an instance of hashing
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

@app.route("/view_gardeners_only", methods=["GET","POST"])
@logged_in
def view_gardeners_only():
    if request.method == "GET":
        cursor, connection = getCursor()
        cursor.execute("SELECT first_name, last_name, address, username, email, phone_number, date_joined, status "
                        "FROM Gardener "
                        "ORDER BY Gardener.first_name;")
        manage_users = cursor.fetchall()
        cursor.close()
        connection.close()
        return render_template("view_gardeners_only.html", manage_users=manage_users)

    
@app.route("/view_users", methods=["GET","POST"])
@logged_in
def view_users():
    if request.method == "GET":
        cursor, connection = getCursor()
        cursor.execute("SELECT first_name, last_name, address, username, email, phone_number, date_joined, status, gardener_id "
                        "FROM Gardener "
                        "ORDER BY Gardener.first_name;")
        manage_users = cursor.fetchall()
        cursor.close()
        connection.close()
        return render_template("manage_users.html", manage_users=manage_users)
    elif request.method == "POST":
        # Handle POST requests if needed
        firstname = request.form['first_name']
        lastname = request.form['last_name']
        address = request.form['address']
        username = request.form['username']
        phonenumber = request.form['phone_number']
        email = request.form['email']
        
        # Update the user's profile information in the database
        cursor, connection = getCursor()
        cursor.execute('UPDATE Gardener SET first_name = %s, last_name = %s, address = %s, username = %s, phone_number = %s, email = %s WHERE gardener_id = %s', (firstname, lastname, address, username, phonenumber, email))
        connection.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('manage_users'))  # Redirect to the Gardener list page after update

@app.route("/view_staff", methods=["GET","POST"])
@logged_in
def view_staff():
    if request.method == "GET":
        cursor, connection = getCursor()
        cursor.execute("SELECT staff_id, first_name, last_name, email, username, work_phone_number, hire_date, position, department, status "
                        "FROM Staff "
                        "ORDER BY Staff.first_name;")
        manage_staff = cursor.fetchall()
        cursor.close()
        connection.close()
        return render_template("manage_staff.html", manage_staff=manage_staff)
    elif request.method == "POST":
        # Handle POST requests if needed
        firstname = request.form['first_name']
        lastname = request.form['last_name']
        email = request.form['email']
        username = request.form['username']
        workphonenumber = request.form['work_phone_number']
        hiredate = request.form['hire_date']
        position = request.form['position']
        department = request.form['department']
        
        # Update the user's profile information in the database
        cursor, connection = getCursor()
        cursor.execute('UPDATE Staff SET first_name = %s, last_name = %s, email = %s, username = %s, work_phone_number = %s, hire_date = %s, position = %s, department = %s  WHERE staff_id = %s', (firstname, lastname, email, username, workphonenumber, hiredate, position, department))
        connection.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('manage_staff'))  # Redirect to the Staff list page after update
    
@app.route('/edit_gardener_profile/<int:gardener_id>', methods=['GET', 'POST'])
@logged_in
def edit_gardener_profile(gardener_id):
    if request.method == 'GET':
        cursor, connection = getCursor()
        cursor.execute('SELECT * FROM Gardener WHERE gardener_id = %s', (gardener_id,))
        account = cursor.fetchone()
        cursor.close()
        connection.close()
        return render_template('edit_user.html', account=account)

    elif request.method == 'POST':
        # Fetch the updated profile information from the form
        firstname = request.form['first_name']
        lastname = request.form['last_name']
        address = request.form['address']
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashing.hash_value(password, salt='abcd')
        phonenumber = request.form['phone_number']
        email = request.form['email']
        datejoined = request.form['date_joined']
        status = request.form['status']
        
        # Update the user's profile information in the database
        cursor, connection = getCursor()
        cursor.execute('UPDATE Gardener SET first_name = %s, last_name = %s, address = %s, username = %s, password = %s, phone_number = %s, email = %s, date_joined = %s, status = %s WHERE gardener_id = %s', (firstname, lastname, address, username, hashed_password, phonenumber, email, datejoined, status, gardener_id))
        connection.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('edit_gardener_profile', gardener_id=gardener_id))  # Redirect to profile page after update

@app.route('/edit_staff_profile/<int:staff_id>', methods=['GET', 'POST'])
@logged_in
def edit_staff_profile(staff_id):
    if request.method == 'GET':
        cursor, connection = getCursor()
        cursor.execute('SELECT * FROM Staff WHERE staff_id = %s', (staff_id,))
        account = cursor.fetchone()
        cursor.close()
        connection.close()
        return render_template('edit_staff.html', account=account)

    elif request.method == 'POST':
        # Fetch the updated profile information from the form
    
        firstname = request.form['first_name']
        lastname = request.form['last_name']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashing.hash_value(password, salt='abcd')
        workphonenumber = request.form['work_phone_number']
        hiredate = request.form['hire_date']
        position = request.form['position']
        department = request.form['department']
        status = request.form['status']
        
        # Update the user's profile information in the database
        cursor, connection = getCursor()
        cursor.execute('UPDATE Staff SET first_name = %s, last_name = %s, email = %s, username = %s, password = %s, work_phone_number = %s, hire_date = %s, position = %s, department = %s, status = %s WHERE staff_id = %s', (firstname, lastname, email, username, hashed_password, workphonenumber, hiredate, position, department, status, staff_id))
        connection.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('edit_staff_profile', staff_id=staff_id))  # Redirect to profile page after update

# Define route to handle deletion of gardeners
@app.route('/delete_gardener/<int:gardener_id>', methods=['POST'])
@logged_in
def delete_gardener(gardener_id):
    if 'delete_gardener' in request.form:
        # Handle deletion of the gardener with the specified ID
        cursor, connection = getCursor()
        cursor.execute('DELETE FROM Gardener WHERE gardener_id = %s', (gardener_id,))
        connection.commit()
        flash('Gardener deleted successfully', 'success')
        cursor.close()
        connection.close()

    return redirect(url_for('view_users', gardener_id=gardener_id))  # Redirect to the Gardener list page

@app.route('/delete_staff/<int:staff_id>', methods=['POST'])
@logged_in
def delete_staff(staff_id):
    if 'delete_staff' in request.form:
        # Handle deletion of the gardener with the specified ID
        cursor, connection = getCursor()
        cursor.execute('DELETE FROM Staff WHERE staff_id = %s', (staff_id,))
        connection.commit()
        flash('Staff deleted successfully', 'success')
        cursor.close()
        connection.close()

    return redirect(url_for('view_staff', staff_id=staff_id))  # Redirect to the Gardener list page