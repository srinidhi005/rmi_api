from flask import Flask,request
from flask_cors import CORS
import json

from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash


from db_connection import db_connect,local_db_connect
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
                return  json_string
            else:
                return '{"Error":"DB Connection Error"}'
        except:
            return '{"Error":"Something went wrong,Make sure that ur passing company name in query params"}'

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

                return str(request.json)
                con.close()  # close database connection
            else:
                return '{"Error":"DB Connection Error"}'

        except Exception as e:
            return '{"Error":'+str(e)+'}'

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
                return  json_string
            else:
                return '{"Error":"DB Connection Error"}'
        except:
            return '{"Error":"Something went wrong,Make sure that ur passing company name in query params"}'

@app.route('/statements' , methods=['GET'])
@auth.login_required
def statements_api():
    if request.method == "GET":
        try:
            con = local_db_connect() #connct to database
            if con is not None:
                cursor = con.cursor()
                query = "select * from statement where order by id desc"
                cursor.execute(query)
                rows = cursor.fetchall()
                field_names = [i[0] for i in cursor.description]
                json_string = json.dumps(
                    [{description: value for description, value in zip(field_names, row)} for row in rows],
                    sort_keys=False, default=str)
                con.close()  # close database connection
                return  json_string
            else:
                return '{"Error":"DB Connection Error"}'
        except:
            return '{"Error":"Something went wrong,Make sure that ur passing company name in query params"}'
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8000,debug=True)
