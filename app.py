import io
import csv
from flask import (
    Flask,
    render_template,
    request,
    flash,
)
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = b"asdf;lkj1234567890"

app.config["MYSQL_HOST"] = "us-cdbr-east-02.cleardb.com"
app.config["MYSQL_USER"] = "bbd5c9ff81e3c1"
app.config["MYSQL_PASSWORD"] = "d6be6e85"
app.config["MYSQL_DB"] = "heroku_72bef458f9f5c50"

mysql = MySQL(app)


@app.route("/")
def index():
    return """
        <html>
            <body>
            <div style="padding-top: 250px; ">
                <h1 style="text-align: center; font-size: 2em;"> Extract data from CSV</h1>

                <form action="/upload" method="post" enctype="multipart/form-data" >
                    <div align="center" >
                        <input type="file" name="data_file" style="font-size:1em;"/>
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
    cur = mysql.connection.cursor()

    csvfile = request.files["data_file"]
    if not csvfile:
        return "No file"

    stream = io.StringIO(csvfile.stream.read().decode("UTF8"), newline=None)
    data = csv.reader(stream)

    next(data)  # skip first line of csv file
    for row in data:
        orderDate = row[0]
        region = row[1]
        rep = row[2]
        item = row[3]
        units = row[4]
        unitCost = row[5]
        total = row[6]

        cur.execute(
            "INSERT INTO csv_data (orderDate, region, rep, item, units, unitCost, total) \
                VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (orderDate, region, rep, item, units, unitCost, total),
        )

        cur.execute("SELECT * FROM csv_data")
        table_data = cur.fetchall()

    field_names = [i[0] for i in cur.description]
    mysql.connection.commit()
    cur.close()

    flash("File uploaded successfully")
    return render_template(
        "index.html", output_data=table_data, field_names=field_names
    )


if __name__ == "__main__":
    app.run(debug=True)
