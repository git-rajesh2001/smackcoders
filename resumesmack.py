from flask import Flask, render_template, request, jsonify
from flask import redirect, url_for
from flask import redirect, request
import mysql.connector
import warnings
from pyresparser import ResumeParser

app = Flask(__name__)

warnings.filterwarnings("ignore", category=UserWarning)

mysql_config = {
    "host": "localhost",
    "user": "root",
    "password": "smackcoders",
    "database": "blue",
    "table": "resume"
}

def save_to_database(data):
    try:
        cnx = mysql.connector.connect(user=mysql_config["user"],
                                      password=mysql_config["password"],
                                      host=mysql_config["host"],
                                      database=mysql_config["database"])
        cursor = cnx.cursor()
        cursor.execute(f'SELECT COUNT(*) FROM {mysql_config["table"]} WHERE email = "{data["email"]}"')
        result = cursor.fetchone()
        if result[0] == 0:  
            query = f'''
                INSERT INTO {mysql_config["table"]} (name, email, skills, designation, education, phone)
                VALUES ("{data["name"]}", 
                "{data["email"]}",
                "{data["skills"]}",
                "{data["designation"]}",
                "{data["education"]}",
                "{data["phone"]}");
            '''
            cursor.execute(query)
            cnx.commit()

    except Exception as e:
        print(f"Error: {e}")

    finally:
        cursor.close()
        cnx.close()


@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    try:
        cnx = mysql.connector.connect(user=mysql_config["user"],
                                      password=mysql_config["password"],
                                      host=mysql_config["host"],
                                      database=mysql_config["database"])
        cursor = cnx.cursor()

        query = f'''
            DELETE FROM {mysql_config["table"]}
            WHERE id = {id};
        '''

        cursor.execute(query)
        cnx.commit()

    except Exception as e:
        print(f"Error: {e}")

    finally:
        cursor.close()
        cnx.close()

    return redirect(request.referrer)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        resume_file = request.files['resume']
        resume_file.save(resume_file.filename)
        data = ResumeParser(resume_file.filename).get_extracted_data()

        name = data.get("name", "")
        email = data.get("email", "")
        skills = data.get("skills", [])
        designation = data.get("designation", "")
        education = data.get("degree", "")
        phone = data.get("mobile_number", "")
        
        skills_str = ", ".join(skills)

        data_dict = {
            "name": name,
            "email": email,
            "skills": skills_str,
            "designation": designation,
            "education": education,
            "phone": phone,
        }

        save_to_database(data_dict)
        return redirect(url_for('index'))

    try:
        cnx = mysql.connector.connect(user=mysql_config["user"],
                                      password=mysql_config["password"],
                                      host=mysql_config["host"],
                                      database=mysql_config["database"])
        cursor = cnx.cursor(dictionary=True)
        cursor.execute(f'SELECT * FROM {mysql_config["table"]}')
        data_from_mysql = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching data from MySQL: {e}")
        data_from_mysql = []

    return render_template('frontend.html', data_from_mysql=data_from_mysql)

@app.route('/delete-all', methods=['POST'])
def delete_all():
    try:
        cnx = mysql.connector.connect(user=mysql_config["user"],
                                      password=mysql_config["password"],
                                      host=mysql_config["host"],
                                      database=mysql_config["database"])
        cursor = cnx.cursor()

        query = f'''
            DELETE FROM {mysql_config["table"]};
        '''

        cursor.execute(query)
        cnx.commit()

    except Exception as e:
        print(f"Error: {e}")

    finally:
        cursor.close()
        cnx.close()

    return redirect(request.referrer)

if __name__ == '__main__':
    app.run(debug=True)
