from flask import Flask, request, render_template, flash,  redirect, url_for, send_from_directory, send_file, session
from werkzeug.utils import secure_filename
from joblib import load
import pandas as pd
import os
import sqlite3
from datetime import datetime
# from flaskwebgui import FlaskUI



##querry for creating table
sql = '''CREATE TABLE IF NOT EXISTS USERS(
    FIRST_NAME CHAR(20) NOT NULL,
    LAST_NAME CHAR(20),
    PASSWORD CHAR(20),
    EMAIL CHAR(20)
)'''

##Databse
conn = sqlite3.connect("records/HeartDisease.db")
cursor = conn.cursor()
cursor.execute(sql)
conn.commit()
cursor.close()
conn.close()


model = load('rf_n100_86.pkl')

UPLOAD_FOLDER = './fileUploads'
ALLOWED_EXTENSIONS = {'csv'}
FILEPATH = ''

app = Flask('app')
app.debug = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# ui = FlaskUI(app , width=1920 , height=1080 , fullscreen=True , host='192.168.0.106' )


def check_user(page):
    if session.get("username"):
        return page
    else:
        return 'login.html'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def Home():
    page = check_user("home.html")
    # ui.run()
    # print(ui)
    # print(ui.fullscreen)
    
    return render_template(page)


@app.route('/info', methods=['GET', 'POST'])
def Info():
    page = check_user("info.html")
    return render_template(page)

@app.route('/heart_report', methods=['GET', 'POST'])
def heart_report():
    page = check_user("index.html")
    if page == 'login.html':
        return render_template('login.html')
    return render_template('heart_report.html')


@app.route('/about', methods=['GET', 'POST'])
def About():
    page = check_user("about.html")
    return render_template(page)


@app.route('/singleReport', methods=['GET', 'POST'])
def SingleReport():
    page = check_user("index.html")
    if page == 'login.html':
        return render_template('login.html')
    if request.method == 'POST':
        try:
    #         ['age', 'sex', 'chest_pain_type', 'resting_blood_pressure',
    #    'cholesterol', 'fasting_blood_sugar', 'rest_ecg',
    #    'max_heart_rate_achieved', 'exercise_induced_angina', 'st_depression',
    #    'st_slope', 'num_major_vessels', 'thalassemia', 'target']

            age = int(request.form['age'])
            sex = str(request.form['sex'])
            chest_pain_type = str(request.form['chest_pain_type'])
            resting_blood_pressure = int(request.form['resting_blood_pressure'])
            cholesterol = int(request.form['cholesterol'])
            fasting_blood_sugar = str(request.form['fasting_blood_sugar'])
            rest_ecg = str(request.form['rest_ecg'])
            max_heart_rate_achieved = int(request.form['max_heart_rate_achieved'])
            exercise_induced_angina = str(request.form['exercise_induced_angina'])
            st_depression = float(request.form['st_depression'])
            st_slope = str(request.form['st_slope'])
            num_major_vessels = int(request.form['num_major_vessels'])
            thalassemia = str(request.form['thalassemia'])

            r1 = {'age': age,
                  'sex': sex,
                  'chest_pain_type': chest_pain_type,
                  'resting_blood_pressure': resting_blood_pressure,
                  'cholesterol': cholesterol,
                  'fasting_blood_sugar': fasting_blood_sugar,
                  'rest_ecg': rest_ecg,
                  'max_heart_rate_achieved': max_heart_rate_achieved,
                  'exercise_induced_angina': exercise_induced_angina,
                  'st_depression': st_depression,
                  'st_slope': st_slope,
                  'num_major_vessels': num_major_vessels,
                  'thalassemia': thalassemia}

            r2 = [age, sex, chest_pain_type, resting_blood_pressure, cholesterol, fasting_blood_sugar, rest_ecg,  max_heart_rate_achieved, exercise_induced_angina,  st_depression, st_slope,  num_major_vessels, thalassemia]
            
            print(r1)
            res = model.predict(pd.DataFrame([[age, sex, chest_pain_type, resting_blood_pressure, cholesterol, fasting_blood_sugar, rest_ecg, max_heart_rate_achieved, exercise_induced_angina, st_depression,st_slope, num_major_vessels, thalassemia]] , columns=['age', 'sex', 'chest_pain_type', 'resting_blood_pressure','cholesterol', 'fasting_blood_sugar', 'rest_ecg','max_heart_rate_achieved', 'exercise_induced_angina', 'st_depression','st_slope', 'num_major_vessels', 'thalassemia']))
            
            if res[0]:
                result = ('You should consult a Doctor.', 1)
            else:
                result = ('Your heart is totally fine.', 0)

            print(result)
            return render_template('singletest.html', result=result,  details = r1)
        except Exception as e:
            result = ('Please pass proper input', 2)
            return render_template('singletest.html', result=result)

    return render_template('singletest.html')


@app.route('/bulkReport', methods=['GET', 'POST'])
def BulkReport():
    page = check_user("index.html")
    if page == 'login.html':
        return render_template('login.html')
    global FILEPATH
    if request.method == 'POST':
        try:
            # check if the post request has the file part
            if 'file' not in request.files:
                res = ('No file part' , 2)
                print('No file part')
                return render_template('bulktest.html', result = res )

            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                res = ('No selected file' , 0)
                print('No selected file')
                return render_template('bulktest.html', result = res )

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                print('1', filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) 
                print('path' , os.path.join(app.config['UPLOAD_FOLDER']) + '/'+filename )
                FILEPATH = os.path.join(app.config['UPLOAD_FOLDER']) + '/'+filename   
                data = pd.read_csv(FILEPATH)
                print(data)
                
                if 'target' in data.columns :
                    tar = data['target']
                    data.drop(columns= ['target'] , inplace = True)

                cols = ['age', 'sex', 'chest_pain_type', 'resting_blood_pressure', 'cholesterol', 'fasting_blood_sugar', 'rest_ecg',
                    'max_heart_rate_achieved', 'exercise_induced_angina', 'st_depression', 'st_slope', 'num_major_vessels', 'thalassemia']
                
                print(list(data.columns))
                if list(data.columns) == cols : 
                                    
                    res = ('Successfully Uploaded' , 1)
                    op = model.predict( data )
                    # print('tar:', tar)
                    print('op:', op)
                    data['Prediction'] = op
                    data.to_csv(FILEPATH , index = False)
                   
                    return  render_template('bulktest.html', result = res , data = [data] )
                else:
                    res = ('Columns in the file were not properly alinged' , 0)
                    return render_template('bulktest.html', result=res)
    

        except:
            result = ('Not a valid File format' , 2)
            return render_template('bulktest.html', result=result )
    
    return render_template('bulktest.html')


@app.route('/download', methods=['POST'])
def downloadFile ():
    page = check_user("index.html")
    if page == 'login.html':
        return render_template('login.html')
    global FILEPATH
    print('filepath', FILEPATH)
    if request.method == 'POST' and FILEPATH != '' :
        return send_file(FILEPATH, as_attachment=True)
    else:
        result = ('Download not possible' , 2)
        return render_template('bulktest.html', result=result )


@app.route('/downloadSample', methods=['POST'])
def downloadSampleFile ():
    page = check_user("index.html")
    if page == 'login.html':
        return render_template('login.html')
    global FILEPATH
    print('filepath', FILEPATH)
    if request.method == 'POST':
        samplefile = os.path.join(app.config['UPLOAD_FOLDER']) + '/'+'samplefile.csv' 
        
        # return render_template('bulktest.html', result=result )
        return send_file( samplefile , as_attachment=True)
    else:
        result = ('Download not possible' , 2)
        return render_template('bulktest.html', result=result )


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    page = check_user("index.html")
    if page == 'login.html':
        return render_template('login.html')
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/EDA', methods=['GET', 'POST'])
def eda():
    page = check_user("index.html")
    if page == 'login.html':
        return render_template('login.html')
    return render_template('eda.html')


@app.route('/HeartDiseaseDataEnge', methods=['GET', 'POST'])
def HeartDiseaseDataEnge():
    page = check_user("index.html")
    if page == 'login.html':
        return render_template('login.html')
    return render_template('HeartDiseaseDataEnge.html')





@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        conn = sqlite3.connect("records/HeartDisease.db")
        cursor = conn.cursor()
        email = str(request.form['email'])
        password = str(request.form["password"])
        mydoc = cursor.execute("SELECT * from USERS WHERE EMAIL = ? AND PASSWORD = ?", (email, password))
        myresult = mydoc.fetchone()
        cursor.close()
        conn.close()
        if myresult:
            session['username'] = str(myresult[0])+" "+str(myresult[1])
            session['email'] = str(myresult[3])
            return redirect('/')
        else:
            return render_template('login.html', msg='email id or password is not matching')


@app.route("/sign", methods=["GET", "POST"])
def sign():
    if request.method == "POST":
        conn = sqlite3.connect("records/HeartDisease.db")
        cursor = conn.cursor()
        fname = str(request.form["fname"])
        lname = str(request.form["lname"])
        password = str(request.form["password"])
        email = str(request.form['email'])
        cursor.execute("SELECT * from USERS WHERE EMAIL = ?", (str(email),))
        if cursor.fetchall():
            return render_template("sign.html", msg="Email Already Exist Try Different")
        else:
            cursor.execute("INSERT INTO USERS(FIRST_NAME, LAST_NAME, PASSWORD, EMAIL) VALUES (?, ?, ?, ?)",
                           (str(fname), str(lname), str(password), str(email)))
            conn.commit()
            session['username'] = str(fname)+" "+str(lname)
            session['email'] = str(email)
        cursor.close()
        conn.close()
        return redirect('/')


@app.route("/login_page", methods=["GET", "POST"])
def login_page():
    return render_template('login.html')


@app.route("/sign_page", methods=["GET", "POST"])
def sign_page():
    return render_template('sign.html')


@app.route('/logout', methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect('/login_page')

@app.route('/links', methods=['GET', 'POST'])
def links():
    page = check_user("links.html")
    return render_template(page)


if __name__ == "__main__":    
    app.run(debug=False)
    # app.run(host='192.168.0.106', port=8080, debug=False )
    # ui.run()
