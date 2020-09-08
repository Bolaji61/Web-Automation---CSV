import io 
import csv
from flask import (
    Flask,
    render_template,
    request,
    flash,
)
from flask_mysqldb import MySQL
import re

app = Flask(__name__)
app.secret_key = "some_random_key"

app.config["MYSQL_HOST"] = "us-cdbr-east-02.cleardb.com"
app.config["MYSQL_USER"] = "bbd5c9ff81e3c1"
app.config["MYSQL_PASSWORD"] = "d6be6e85"
app.config["MYSQL_DB"] = "heroku_72bef458f9f5c50"

mysql = MySQL(app)


@app.route("/")
def index():
    #render html template
    return """
        <html>
            <body>
            <div style="padding-top: 10px; padding-left: 20px; ">
                <h1 style="text-align: left; font-size: 2em;"> Extract data from CSV</h1>

                <form action="/upload" method="post" enctype="multipart/form-data" >
                    <div align="left" >
                        <input type="file" name="data_file" style="font-size:1em;"/>
                        <br>
                        <br>
                        <input type="submit" name="csv_upload_btn" value="Upload" style="font-size:0.8em;"/>
                    </div>
                </form>
            </div>
            </body>
        </html>
    """


@app.route("/upload", methods=["POST"])
def upload():
    """
    Returns: Webpage showing table form of csv input
    """

    cur = mysql.connection.cursor()  #connect to mysql

    csvfile = request.files["data_file"] #import csv data
    if not csvfile:
            return "No file"
    stream = io.StringIO(csvfile.stream.read().decode("UTF8"), newline=None)
    data = list(csv.reader(stream))
    field_names, first_row = data[0:2]
    field_names = convert_to_snakecase(field_names)
    field_types = determine_field_type(first_row)
    table_name = convert_to_snakecase([csvfile.filename])[0]
 
    res = []
    for k, j in zip(field_names, field_types):
        res.append("{} {}".format(k, j))
    fields = ", ".join(res)
    create_query = "CREATE TABLE IF NOT EXISTS {} ({})".format(table_name, fields)
    cur.execute(create_query)

    insert_query = "INSERT INTO {} ({}) VALUES ({})".format(table_name, ", ".join(field_names), ", ".join(["%s"] * len(field_names)))
    data_to_insert = []

    for row in data[1:]:
        data_to_insert.append(tuple(row))

    cur.executemany(insert_query, data_to_insert)

    #execute SQL statements
    cur.execute("SELECT * FROM {}".format(table_name))
    table_data = cur.fetchall()  #fetch all data in table database

    mysql.connection.commit()
    cur.close()

    flash(message="File uploaded successfully") #flash message
    return render_template(
        "index.html", output_data=table_data, field_names=field_names
    )


def convert_to_snakecase(field_names = []):
    escaped_field_names = []
    for col_name in field_names:
        output = re.sub('[^0-9a-zA-Z]+', "_", col_name)
        escaped_field_names.append(output)
    return escaped_field_names


def determine_field_type(first_row = []):
    data_types = []
    for col in first_row:
        _type = ""
        try:
            float(col)
            _type = "FLOAT"
            try:
                int(col)
                _type = "INT"
            except: pass
        except ValueError:
            _type = "VARCHAR(255)"
        data_types.append(_type)
    return data_types


if __name__ == "__main__":
    app.run(debug=True)
