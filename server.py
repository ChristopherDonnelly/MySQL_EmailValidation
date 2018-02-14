from flask import Flask, request, redirect, render_template, session, flash, url_for
from mysqlconnection import MySQLConnector
import re
import datetime
import time

# Email Regular Expression
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

app = Flask(__name__)

mysql = MySQLConnector(app,'email_validation')

app.secret_key = 'EmailValidationKey'

@app.route('/')

def display_index():   
    session['method'] = ''
    return render_template('index.html')

@app.route('/results', methods=['POST'])
def results():

    valid = True

    session['email'] = email = request.form['email']

    if len(email) < 1:
        flash("Email cannot be blank!", 'red')
        valid = False
    elif not EMAIL_REGEX.match(email):
        flash("Invalid Email Address!", 'red')
        valid = False
    else:
        flash("hidden", "hidden")
    
    if valid:

        # Determine if email already exists in DB
        verifyQuery = "SELECT count(id) as count FROM emails where address = (:address)"
        data = {
                'address': email
            }
        exists = mysql.query_db(verifyQuery, data)

        # If email does not exist then add it to DB
        if(not int(exists[0]['count'])):

            insertQuery = "INSERT INTO emails (address, created_at, updated_at) VALUES (:address, NOW(), NOW())"
            
            data = {
                    'address': email
                }
            
            mysql.query_db(insertQuery, data)
            
            session['method'] = ' added a VALID '

            return redirect('/success')
        else:
            flash("Error, email already exist!", 'red')
            return redirect('/')

    else:
        return redirect('/')

@app.route('/success')
def success():
    query = "SELECT id, address, DATE_FORMAT(created_at, '%m/%d/%Y') as date, DATE_FORMAT(created_at, '%r') as time FROM emails"
    emails = mysql.query_db(query)

    if 'email' in session:
        email = session.pop('email')
    else:
        email = 'None'

    if 'method' in session:
        methodMsg = session.pop('method')
    else:
        methodMsg = ''

    methodMsg = 'You have successfully {} email address ({})! Thank you!'.format(methodMsg, email)

    return render_template('success.html', all_emails = emails, email = email, methodMsg = methodMsg)

@app.route('/home', methods=['POST'])
def redirect_url(default='display_index'):

    if 'delete' in request.form:
        if request.form['delete'] == 'D':
            query = "DELETE FROM emails WHERE id = :id"
            data = {'id': request.form['id']}
            mysql.query_db(query, data)

            session['email'] = request.form['address']
            session['method'] = ' deleted the '

            return redirect(url_for('success'))
          
    return redirect(url_for(default))

app.run(debug=True)