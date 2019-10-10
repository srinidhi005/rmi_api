from flask import Flask,request
from flask_cors import CORS
import json

from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash


from db_connection import db_connect
app = Flask(__name__)
CORS(app)
auth = HTTPBasicAuth()
users = {
    "rmi_user": generate_password_hash("rmi321!@#"),
    "test_user": generate_password_hash("test321#")
}

@auth.verify_password
def verify_password(username, password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False

@app.route('/actuals')
@auth.login_required
def actuals_api():
    try:
        company = request.args['company']
        con = db_connect() #connct to database
        if con is not None:
            cursor = con.cursor()
            query = "select * from company_actuals where companyname='"+company+"'"
            cursor.execute(query)
            rows = cursor.fetchall()
            field_names = [i[0] for i in cursor.description]
            json_string = json.dumps([{description: value for description, value in zip(field_names, row)} for row in rows],sort_keys=True, default=str)
            con.close() #close database connection
            return  json_string
        else:
            return '{"Error":"DB Connection Error"}'
    except:
        return '{"Error":"Something went wrong,Make sure that ur passing company name in query params"}'

@app.route('/projections' , methods=['GET','POST'])
@auth.login_required
def projections_api():
    if request.method == "GET":
        try:
            company = request.args['company']
            con = db_connect() #connct to database
            if con is not None:
                cursor = con.cursor()
                query = "select * from company_projections where companyname='"+company+"'"
                cursor.execute(query)
                rows = cursor.fetchall()
                field_names = [i[0] for i in cursor.description]
                json_string = json.dumps([{description: value for description, value in zip(field_names, row)} for row in rows],sort_keys=True, default=str)
                con.close() #close database connection
                return  json_string
            else:
                return '{"Error":"DB Connection Error"}'
        except:
            return '{"Error":"Something went wrong,Make sure that ur passing company name in query params"}'

    if request.method == "POST":
        con = db_connect()  # connct to database
        try:
            contents = request.json
            for content in contents:
                company = content["companyname"]
                asof = content["asof"]

            if con is not None:
                cursor = con.cursor()
                query = "delete from company_projections where companyname='" + company + "' and asof='" + asof + "'"
                cursor.execute(query)
                con.commit()
                query = "insert into company_projections(comapanyname,asof) values('" + company + "', asof='" + asof + "') where companyname='"+company+"' and asof='" + asof + "'"
                cursor.execute(query)
                con.commit()
                con.close() #close database connection
                return  contents
            else:
                return '{"Error":"DB Connection Error"}'
        except:
            return '{"Error":"Something went wrong,Make sure that ur passing company name in query params"}'
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8000,debug=True)
