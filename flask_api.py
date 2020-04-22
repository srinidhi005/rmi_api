from flask import Flask,request
from flask_cors import CORS
import json
from werkzeug.utils import secure_filename
import os
import datetime

UPLOAD_FOLDER = '/home/rmi_api/uploads'

from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash


from db_connection import db_connect,local_db_connect
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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

json_return = {
    "code":0,
    "message":"None",
    "description":"",
    "result":""
}


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
            json_return["code"] = 200
            json_return["message"] = "Success"
            json_return["description"] = "company_actuals list"
            json_return["result"] = json_string
            # return json.dumps(json_return)
            return  json_string
        else:
            json_return["code"] = 500
            json_return["message"] = "Fail"
            json_return["description"] = "DB Connection Error"
            json_return["result"] = []
            # return json.dumps(json_return)
            return '{"Error":"DB Error"}'
    except Exception as e:
        json_return["code"] = 500
        json_return["message"] = "Fail"
        json_return["description"] = str(e)
        json_return["result"] = []
        # return json.dumps(json_return)
        return '{"Error":"Something went wrong,Make sure that ur passing company name in query params"}'

@app.route('/projections' , methods=['GET','POST'])
@auth.login_required
def projections_api():
    if request.method == "GET":
        try:
            company = request.args['company']
            scenario = request.args['scenario']
            con = db_connect() #connct to database
            if con is not None:
                cursor = con.cursor()
                query = "select * from company_projections where companyname='"+company+"' and scenario='"+str(scenario)+"'"
                cursor.execute(query)
                rows = cursor.fetchall()
                field_names = [i[0] for i in cursor.description]
                json_string = json.dumps([{description: value for description, value in zip(field_names, row)} for row in rows],sort_keys=True, default=str)
                con.close() #close database connection
                json_return["code"] = 200
                json_return["message"] = "Success"
                json_return["description"] = "company_projections list"
                json_return["result"] = json_string
                # return json.dumps(json_return)
                return json_string
            else:
                json_return["code"] = 500
                json_return["message"] = "Fail"
                json_return["description"] = "DB Connection Error"
                json_return["result"] = []
                # return json.dumps(json_return)
                return '{"Error":"DB Error"}'
        except Exception as e:
            json_return["code"] = 500
            json_return["message"] = "Fail"
            json_return["description"] = str(e)
            json_return["result"] = []
            # return json.dumps(json_return)
            return {"Error":str(e)}

    if request.method == "POST":
        con = db_connect()  # connct to database
        try:
            if con is not None:
                cursor = con.cursor()
                contents = request.json
                for content in contents:
                    company = content["companyname"]
                    asof = content["asof"]
                    scenario = content["scenario"]
                    latest = content["latest"]
                    totalrevenue = content["totalrevenue"]
                    cogs = content["cogs"]
                    grossprofit = content["grossprofit"]
                    sga = content["sga"]
                    ebit = content["ebit"]
                    ebitmargin = content["ebitmargin"]
                    da = content["da"]
                    ebitda = content["ebitda"]
                    ebitdamargin = content["ebitdamargin"]
                    netinterest = content["netinterest"]
                    otherincome = content["otherincome"]
                    ebt = content["ebt"]
                    ebtmargin = content["ebtmargin"]
                    taxes = content["taxes"]
                    netincome = content["netincome"]
                    netincomemargin = content["netincomemargin"]
                    revenuepercent = content["revenuepercent"]
                    cogspercent = content["cogspercent"]
                    sgapercent = content["sgapercent"]
                    dapercent = content["dapercent"]
                    netinterestdollars = content["netinterestdollars"]
                    otherincomepercent = content["otherincomepercent"]
                    taxespercent = content["taxespercent"]
                    grossprofitmargin = content["grossprofitmargin"]




                    query = "delete from company_projections where companyname='" + company + "' and asof=" + str(asof) + " and scenario='" + str(scenario) + "'"
                    print(query)
                    cursor.execute(query)
                    con.commit()
                    query = "insert into company_projections(companyname,asof,scenario,totalrevenue,latest,cogs,grossprofit,grossprofitmargin,sga," \
                            "ebit,ebitmargin,da,ebitda,ebitdamargin,netinterest,otherincome,ebt,ebtmargin,taxes,netincome,netincomemargin,revenuepercent," \
                            "cogspercent,sgapercent,dapercent,netinterestdollars,otherincomepercent,taxespercent) values('" + company + "'," + str(asof) + "," \
                           "'"+str(scenario)+"',"+str(totalrevenue)+","+str(latest)+","+str(cogs)+","+str(grossprofit)+","+str(grossprofitmargin)+"" \
                            ","+str(sga)+","+str(ebit)+","+str(ebitmargin)+","+str(da)+","+str(ebitda)+","+str(ebitdamargin)+"" \
                            ","+str(netinterest)+","+str(otherincome)+","+str(ebt)+","+str(ebtmargin)+","+str(taxes)+","+str(netincome)+"" \
                            ","+str(netincomemargin)+","+str(revenuepercent)+","+str(cogspercent)+","+str(sgapercent)+","+str(dapercent)+","+str(netinterestdollars)+"" \
                            ","+str(otherincomepercent)+","+str(taxespercent)+")"
                    print(query)
                    cursor.execute(query)
                    con.commit()
                json_return["code"] = 200
                json_return["message"] = "Success"
                json_return["description"] = "Updated Scenerios"
                json_return["result"] = str(request.json)
                # return json.dumps(json_return)

                return str(request.json)
                con.close()  # close database connection
            else:
                json_return["code"] = 500
                json_return["message"] = "Fail"
                json_return["description"] = "DB Connection Error"
                json_return["result"] = []
                # return json.dumps(json_return)
                return '{"error":"DB Connection Error"}'
        except Exception as e:
            json_return["code"] = 500
            json_return["message"] = "Fail"
            json_return["description"] = str(e)
            json_return["result"] = []
            # return json.dumps(json_return)
            return {"Error": str(e)}

@app.route('/scenarios' , methods=['GET'])
@auth.login_required
def scenarios_api():
    if request.method == "GET":
        try:
            company = request.args['company']
            con = db_connect() #connct to database
            if con is not None:
                cursor = con.cursor()
                query = "select distinct scenario from company_projections where companyname='"+company+"'"
                cursor.execute(query)
                rows = cursor.fetchall()
                scenarios = [i[0] for i in rows]
                scenarios.sort()
                scenerio = {"scenarios":scenarios}
                json_string = json.dumps(scenerio,sort_keys=True, default=str)
                con.close() #close database connection
                json_return["code"] = 200
                json_return["message"] = "Success"
                json_return["description"] = "Scenerios list"
                json_return["result"] = json_string
                return json_string
                # return json.dumps(json_return)
            else:
                json_return["code"] = 500
                json_return["message"] = "Fail"
                json_return["description"] = "DB Connection Error"
                json_return["result"] = []
                # return json.dumps(json_return)
            return '{"error":"DB Connection Error"}'
        except Exception as e:
            json_return["code"] = 500
            json_return["message"] = "Fail"
            json_return["description"] = str(e)
            json_return["result"] = []
            # return json.dumps(json_return)
            return {"Error": str(e)}

@app.route('/companies' , methods=['GET'])
@auth.login_required
def companies_api():
    if request.method == "GET":
        try:
            con = db_connect() #connct to database
            if con is not None:
                cursor = con.cursor()
                query = "select distinct companyname from company_actuals"
                cursor.execute(query)
                rows = cursor.fetchall()
                companies = [i[0] for i in rows]
                companies.sort()
                companies = {"companies":companies}
                json_string = json.dumps(companies,sort_keys=True, default=str)
                con.close() #close database connection
                json_return["code"] = 200
                json_return["message"] = "Success"
                json_return["description"] = "companies list"
                json_return["result"] = json_string
                return json_string
                # return json.dumps(json_return)
            else:
                json_return["code"] = 500
                json_return["message"] = "Fail"
                json_return["description"] = "DB Connection Error"
                json_return["result"] = []
                # return json.dumps(json_return)
                return '{"error":"DB Connection Error"}'
        except Exception as e:
            json_return["code"] = 500
            json_return["message"] = "Fail"
            json_return["description"] = str(e)
            json_return["result"] = []
            # return json.dumps(json_return)
            return {"Error": str(e)}
@app.route('/statements' , methods=['GET'])
@auth.login_required
def statements_api():
    if request.method == "GET":
        try:
            con = db_connect() #connct to database
            if con is not None:
                cursor = con.cursor()
                #query = "select t1.*,t2.username from statement t1,users t2 where t1.user_id=t2.id order by t1.id desc"
                query = "select * from company_master order by uid desc"
                cursor.execute(query)
                rows = cursor.fetchall()
                field_names = [i[0] for i in cursor.description]
                json_string = json.dumps(
                    [{description: value for description, value in zip(field_names, row)} for row in rows],
                    sort_keys=False, default=str)
                con.close()  # close database connection
                json_return["code"] = 200
                json_return["message"] = "Success"
                json_return["description"] = "statements list"
                json_return["result"] = json_string
                # return json.dumps(json_return)
                return json_string
            else:
                json_return["code"] = 500
                json_return["message"] = "Fail"
                json_return["description"] = "DB Connection Error"
                json_return["result"] = []
                # return json.dumps(json_return)
                return '{"error":"DB Connection Error"}'
        except Exception as e:
            json_return["code"] = 500
            json_return["message"] = "Fail"
            json_return["description"] = str(e)
            json_return["result"] = []
            # return json.dumps(json_return)
            return {"Error": str(e)}

@app.route('/userprofile' , methods=['GET'])
@auth.login_required
def user_profile_api():
    if request.method == "GET":
        try:
            email = request.args['email']
            con = db_connect() #connct to database
            if con is not None:
                cursor = con.cursor()
                query = "select * from user_profile where email='"+email+"'"
                cursor.execute(query)
                rows = cursor.fetchall()
                field_names = [i[0] for i in cursor.description]
                json_string = json.dumps(
                    [{description: value for description, value in zip(field_names, row)} for row in rows],
                    sort_keys=False, default=str)
                con.close()  # close database connection
                json_return["code"] = 200
                json_return["message"] = "Success"
                json_return["description"] = "User Profile"
                json_return["result"] = json_string
                # return json.dumps(json_return)
                return json_string
            else:
                json_return["code"] = 500
                json_return["message"] = "Fail"
                json_return["description"] = "DB Connection Error"
                json_return["result"] = []
                # return json.dumps(json_return)
                return '{"error":"DB Connection Error"}'
        except Exception as e:
            json_return["code"] = 500
            json_return["message"] = "Fail"
            json_return["description"] = str(e)
            json_return["result"] = []
            # return json.dumps(json_return)
            return {"Error": str(e)}

@app.route('/updateprofile' , methods=['POST'])
@auth.login_required
def update_profile_api():
    if request.method == "POST":
        try:
            userName = request.form.get("userName")
            firstName = request.form.get("firstName")
            lastName = request.form.get("lastName")
            email = request.form.get("email")
            password = request.form.get("password")
            contactNumber = request.form.get("contactNumber")
            companyName = request.form.get("companyName")
            companyTitle = request.form.get("companyTitle")
            companyAddress = request.form.get("companyAddress")
            companyCity = request.form.get("companyCity")
            companyState = request.form.get("companyState")
            companyZipCode = request.form.get("companyZipCode")
            companyCountry = request.form.get("companyCountry")
            industry = request.form.get("industry")
            geography = request.form.get("geography")
            companySize = request.form.get("companySize")
            capatialization = request.form.get("capatialization")
            revenue = request.form.get("revenue")
            profileImage = request.files['profileImage']
            companyLogo = request.files['companyLogo']
            if profileImage and companyLogo:
                profile_filename = secure_filename(profileImage.filename)
                logo_filename = secure_filename(companyLogo.filename)
                profile_image_path = os.path.join(app.config['UPLOAD_FOLDER'], profile_filename)
                logo_image_path = os.path.join(app.config['UPLOAD_FOLDER'], logo_filename)
                profileImage.save(profile_image_path)
                companyLogo.save(logo_image_path)
                date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # json_return["code"] = 200
                # json_return["message"] = "Success"
                # json_return["description"] = "File Uploaded Successfully"
                # json_return["result"] = "OK"
                # return json_string
                con = db_connect()  # connct to database

                if con is not None:
                    cursor = con.cursor()

                    try:

                        query = "select * from user_profile where email='"+email+"'"
                        cursor.execute(query)
                        if(len(cursor.fetchall()) > 0): # check if record exist
                            query = "delete from user_profile where email='"+email+"'"
                            cursor.execute(query) # delete existing
                            con.commit() # save

                        query = "insert into user_profile(username,email,firstname,lastname,password,contact," \
                                "companyname,title,address,city,state,country,zipcode,industry,geography,companysize," \
                                "capitalisation,revenue,userimage,companyimage,createdon) values('"+userName+"','"+email+"','"+firstName+"'," \
                               "'"+lastName+"','"+password+"','"+contactNumber+"','"+companyName+"','"+companyTitle+"','"+companyAddress+"'," \
                                "'"+companyCity+"','"+companyState+"','"+companyCountry+"','"+companyZipCode+"','"+industry+"'," \
                                "'"+geography+"','"+companySize+"','"+capatialization+"','"+revenue+"','"+profile_image_path+"'," \
                               "'"+logo_image_path+"','"+date_time+"')"

                        cursor.execute(query)
                        con.commit()
                        return {"Success":"Registration Completed Successfully"}
                    except Exception as e:
                        return {"Error":str(e)}


            else:
                json_return["code"] = 500
                json_return["message"] = "Fail"
                json_return["description"] = "DB Connection Error"
                json_return["result"] = []
                # return json.dumps(json_return)
                return '{"error":"DB Connection Error"}'
        except Exception as e:
            json_return["code"] = 500
            json_return["message"] = "Fail"
            json_return["description"] = str(e)
            json_return["result"] = []
            # return json.dumps(json_return)
            return {"Error": str(e)}

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8000,debug=True)


