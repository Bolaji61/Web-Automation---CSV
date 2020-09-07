import os
import csv
from flask import Flask, render_template, request, make_response, redirect, url_for, flash
from flask_mysqldb import MySQL
import io

app = Flask(__name__)
app.secret_key = b'asdf;lkj1234567890'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'invisible'

mysql = MySQL(app)

@app.route('/')
def index():
    return """
        <html>
            <body>
                <h1>Transform a csv upload</h1>

                <form action="/upload" method="post" enctype="multipart/form-data">
                    <div align="center">
                        <input type="file" name="data_file" />
                        <input type="submit" name="csv_upload_btn" value="Upload" />
                    </div>
                </form>
            </body>
        </html>
    """

@app.route('/upload', methods=["POST"])
def upload():
    csvfile = request.files['data_file']
    if not csvfile:
        return "No file"

    # file_contents = csvfile.stream.read().decode("utf-8")
    stream = io.StringIO(csvfile.stream.read().decode("UTF8"), newline=None)
    data = csv.reader(stream)
    first_line = True
    data_dict = []
    for row in data:
        if not first_line:
            data_dict.append({
                "username": row[0],
                "login_email": row[1],
                "identifier": row[2],
                "first_name": row[3],
                "last_name": row[4]
            })
        else:
            first_line = False

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO csvdata(username, login_email, identifier, first_name, last_name) VALUES (%s, %s, %s, %s, %s)", \
            ("username", "login_email", "identifier", "first_name", "last_name"))
        mysql.connection.commit()
        cur.close()
        
    return "Congrats, you are now a registered user!"

if __name__ == '__main__':
    app.run()
