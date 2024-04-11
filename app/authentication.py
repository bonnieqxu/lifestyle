from app import app
from flask import render_template, request, redirect, url_for, session, flash
import mysql.connector
import app.connect as connect
from flask_hashing import Hashing
from app.utility import logged_in
from app.forms import ChangePasswordForm

hashing = Hashing(app)  # Create an instance of hashing

# Global variables for database connection
dbconn = None
connection = None

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
    return dbconn

# Authentication route for member, tutor, and manager
@app.route('/authentication/', methods=['GET', 'POST'])
def authentication():
    msg = ''
    if request.method == 'POST':
        if 'logout' in request.form:
            session.clear()
            return redirect(url_for('landingpage'))

        elif 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']

            # Check if account exists using MySQL
        cursor = getCursor()
        cursor.execute('SELECT * FROM user WHERE username = %s', (username,))
        # Fetch one record and return result
        account = cursor.fetchone()
        if account is not None:
            hashed_password = account[2]
            if hashing.check_value(hashed_password,password, salt='abcd'):
                if account[4] == 'A':
                # If account exists in accounts table 
                # user have to be in Active status
                # Create session data, we can access this data in other routes
                    session['loggedin'] = True
                    session['id'] = account[0]
                    session['username'] = account[1]
                    session['userrole'] = account[3]
                    session['profileimage'] = ""

                    if session['userrole'] == "MM": #member
                        cursor = getCursor()
                        cursor.execute('SELECT * FROM member WHERE member_id = %s', (session['id'],) )
                        user = cursor.fetchone()
                        session['userfullname'] = user[2] + ' ' + user[3]
                        cursor.close()
                        connection.close()
                        #return render_template('member_home.html')
                        return redirect(url_for('member_home'))
                    
                    elif session['userrole'] == "TT":
                        #redirect to tutor
                        cursor = getCursor()
                        cursor.execute('SELECT * FROM staff WHERE staff_id = %s', (session['id'],) )
                        user = cursor.fetchone()
                        session['userfullname'] = user[2] + ' ' + user[3]
                        cursor.close()
                        connection.close()
                        #return render_template('tutor_home.html')
                        return redirect(url_for('tutor_home'))

                    else:
                        #redirect to manager
                        cursor = getCursor()
                        cursor.execute('SELECT * FROM staff WHERE staff_id = %s', (session['id'],) )
                        user = cursor.fetchone()
                        session['userfullname'] = user[2] + ' ' + user[3]
                        cursor.close()
                        connection.close()
                        #return render_template('manager_home.html')
                        return redirect(url_for('manager_home'))

                else:
                    #Inactive status is not allowed to login
                    msg = 'User is inactive!'
            else:
                #password incorrect
                msg = 'Incorrect password!'
        else:
            # Account doesnt exist or username incorrect
            msg = 'Incorrect username'

    return render_template('login.html', msg=msg)
            
            

@app.route('/logout', methods=['GET'])
def logout():
    msg = session.pop('_flashes', None)
    session.clear()
    if msg is not None:
        for category, message in msg:
            flash(message, category=category)
    return render_template("landing_page.html")

@app.route("/returnchangepassword", methods=['GET'])
@logged_in
def returnchangepassword():
    form=ChangePasswordForm()
    return render_template("changepassword.html", form=form)    
    
@app.route("/changepassword", methods=['POST'])
@logged_in
def changepassword():
    #change password function is used commonly as there is no difference between userrole
    #new password has to be hashed before storing into db
    form=ChangePasswordForm()

    if form.validate_on_submit():
        password = form.password.data
        current_password = form.current_password.data
        hashed = hashing.hash_value(password, salt='abcd')

        #check if current password is entered correctly or not
        cursor = getCursor()
        cursor.execute('SELECT * FROM user WHERE user_id = %s', (session['id'],))
        # Fetch one record and return result
        account = cursor.fetchone()
        if account is not None:
            hashed_password = account[2]
            if hashing.check_value(hashed_password,current_password, salt='abcd'):
                cur = getCursor()
                cur.execute("""UPDATE user SET passwordhash=%s WHERE user_id = %s;""",
                                    ( hashed, session['id'],))
                
                flash('Password changed successfully', category='success')

                return redirect(url_for("logout"))  

            else:
                msg = "Incorrect current password"
                return render_template("changepassword.html", form=form, msg=msg)       
    else:
        return render_template("changepassword.html", form=form)   