import sys
import json
import mysql.connector
import pdfplumber
from google.api_core.client_options import ClientOptions
from google.cloud import automl_v1
from google.cloud.automl_v1.proto import service_pb2
import re,os
import collections
import datetime
from google.cloud import storage



def inline_text_payload(file_path):
  with open(file_path, 'rb') as ff:
    content = ff.read()
  return {'text_snippet': {'content': content, 'mime_type': 'text/plain'} }

def pdf_payload(file_path):
  return {'document': {'input_config': {'gcs_source': {'input_uris': [file_path] } } } }

def get_prediction(file_path, model_name):
  options = ClientOptions(api_endpoint='automl.googleapis.com')
  prediction_client = automl_v1.PredictionServiceClient(client_options=options)

  # payload = inline_text_payload(file_path)
  # Uncomment the following line (and comment the above line) if want to predict on PDFs.
  payload = pdf_payload(file_path)

  params = {}
  request = prediction_client.predict(model_name, payload, params)
  return request  # waits until request is returned


def years_fun(lines):
    # Assuming Sorted False
    IncomeStatementdict = [
                ".*Consolidated.*Statement.*Operations.*",
          ".*Consolidated.*Statement.*of.*Incom.*",
                ".*Consolidated.*Statement.*Inc.*",
                ".*Consolidated.*Statement.*Earnings.*",
                ".*Income Statement.*",
                ]
    sorted = False
    no_of_years = 3
    year_flag = 0 # assuming years not found initially
    for j in IncomeStatementdict:
        count = 0
        for line in lines:
            count +=1
            if re.search(j,line, re.IGNORECASE):
                print("Found Statement of Income")
                break
        
        for line in lines[count:]:
            res=re.findall('[0-9]{4}',line)
            if len(res) >=2:
                year_flag = 1 # years found
                break
        if year_flag:
            break
    if year_flag:
        years = list(map(int,res))   # convert years to numbers
        no_of_years = len(years)
        if no_of_years > 3: # if years more than 3 
            list_years =  years[:]
            list_years.sort()
            if list_years == years: # if years are already sorted & in ascending order
                sorted = True
            if sorted:
                years = years[-3:]    # last 3 years
            else:
                years = years[:3] # first 3 years
        
    else:
        years =  [2017,2016,2015] # Use default years 
        print("Used Default Years=========")
    return years,no_of_years,sorted

def preprocessing(term_list,years,unit_used):
    new_list=[]
    if not term_list or term_list is None or term_list == []:
        for i in years:
            new_list.append(0)
        term_list=new_list
    else:
        term_list = term_list[-len(years):] # take exact no of values as no of years from the right most
        if sorted:
            term_list = term_list[-len(years):]
        else:
            term_list = term_list[:len(years)]
        for ele in term_list:
            ele=ele.replace("(","-")
            ele=ele.replace(")","")
            if unit_used.lower() == "millions":
                new_list.append(float(ele))
            else:
                new_list.append(float(ele)/1000)
        term_list=new_list
    return term_list

def main_function(file_path,model_name,company_name,period,user,industry,statement_type,filename):

    message = "Success"
    try:
        pdftotextlines = ""


        print("=============Program Started============")
        filepath,file1 = os.path.split(file_path)
        pdf_filename = file1.rsplit(".",1)[0]
        print(pdf_filename)

        txt_file_path='/home/srinidhi/angular/ExtractedFiles/'+pdf_filename+'.txt'

        term_dict={}
        total_revenue_patterns = ["Revenues","Net sales","Total revenue","Net revenue","Net Revenue",
        "Net Revenues","Total net sales","Revenues","Total revenues","NET OPERATING REVENUES",
        "Total Net Revenue","Total Revenue","Total Revenues",
        "Revenue","Sales to customer","Net Sale","Net Sales","NET SALES","Net sales",
        "Total net revenues.*","net sales","Total sales","Sales"]
        depriciation_amort=["Depreciation and amortization",
                "Depreciation and amortization of property, equipment and intangibles",
                "Depreciation, amortization, and other",
                "Depreciation and amortization expense",
        "Depreciation and amortization expenses",
                "Depreciation expense",
                "Depreciation",
                ]
        

        url="/home/srinidhi/angular/ExtractedFiles/"+pdf_filename+".pdf"
        try:
            fPDFExtractedText = open(txt_file_path,"w")
            pdf = pdfplumber.open(url)
            table_rows = ""
            for page in pdf.pages:
                text = page.extract_text(x_tolerance=1, y_tolerance=1)
                
                fPDFExtractedText.write("\nPage#" + str(page.page_number))

                fPDFExtractedText.writelines("\n")  
                if text is not None:
                    text = text.replace(u'\xA0', ' ')
                    text = text.replace('  ', ' ')
                    text = re.sub('[. .]{3,100}', ' ', text)
                    fPDFExtractedText.writelines(text)
                    pdftotextlines += text
        except Exception as e:
            print("Error In PDF To Text Conversion to Writing to File",e)
        finally:
            fPDFExtractedText.close() # close the file
        lines = pdftotextlines.split("\n") #split by lines

        
          

        # lines = table_rows.split("\n")

        output_obj = get_prediction(file_path, model_name)

        key_count=len(output_obj.payload)
        # print(output_obj.payload)
        with open('/home/srinidhi/angular/ExtractedFiles/'+pdf_filename+'.json','w') as of:
            of.writelines(str(output_obj.payload))


        for i in range(0,key_count):
          display_name = output_obj.payload[i].display_name
          content = output_obj.payload[i].text_extraction.text_segment.content
          values_list=[]
          score=output_obj.payload[i].text_extraction.score
          values_list.append(content)
          values_list.append(score)
          if term_dict.get(display_name)==None:
            term_dict[display_name]=values_list
          else:
            existing_term=term_dict.get(display_name)
            if score>existing_term[1]:
              term_dict[display_name]=values_list


        dict_final={}
        try:
          years,no_of_years,sorted=years_fun(lines)
          
        except Exception as e:
          print(e,"Exception in Year Fetching")

        sorted_years = years
        sorted_years.sort(reverse=True)



        years_association = {}

        if sorted:
            balance_sheet_years = years[-2:]
        else: 
            balance_sheet_years = years[:2]




        latest_val = 0
        for year in sorted_years:
            years_association[year] = latest_val
            latest_val -= 1

        print(years_association,"\nyears_association=============")  

        count=0

        try:
          Company = term_dict["Company"][0]
        except Exception as e:
          Company='NA'
          print("Comapny Name not found. Marking it \"NA\"")

        ## fetch units ###

        try:
            unit = term_dict.get("Units")
            unit_used = unit[0]
        except Exception as e:
            unit_used = "millions"
            print(e)
            print("=======units not found, using default=======")

        print(unit_used,"=============Units Used============")



        # print(term_dict)

        for key in term_dict.keys():
            for line in lines:#loop through all rows
                
                # line = line.replace("’","") # repalce "\'"
                # line = line.replace("'","") # repalce "\'"
                # line = line.replace("\342\200\231","") # repalce "\'"
                # term = term_dict[key][0].replace("\'","") # repalce "\'"
                # term = term.replace("’","") # repalce "\'"
                line_tmp = re.sub('[\W_]+', '', line)
                term = re.sub('[\W_]+', '', term_dict[key][0])
                # print(line,term)
                
                if term in line_tmp:
                    # print(term_dict[key][0],"============",line)
                    try:
                      line=line.replace(',', '')
                      line=line.replace('$','')
                      values = re.findall("\(?[0-9.]{1,10}\)?", line)
                      if len(values) >= 2:
                          dict_final[key]=values
                          print(key,"========",values)
                    except Exception as e:
                      print("exception in fetching",e)
                    break

        try:
            DandA = term_dict["DandA"][0]
            # print(DandA,"===============DandA")
            if re.search("amortization",DandA,re.IGNORECASE) is None:
                # print("Yes not there")
                amort_flag = 0
            else:
                # print("Amortization present")
                amort_flag = 1
            
        except:
            amort_flag = 1
            pass
        amort = []
        # print(pdftotextlines)
        # print(amort_flag)
        try:
            if not amort_flag:
                for line in lines:
                    
                    # print(line)
                    if line.startswith("Amortization"):
                        line=line.replace(',', '')
                        line=line.replace('$','')
                        # print(line,"line============================")
                        amort = re.findall("\(?[0-9.]{1,10}\)?", line)
                        if len(amort) >= 2:
                            break
        except:
            pass
        print(amort,"Amortization==============")
        AccruedLiabilities = []
        AccruedLiabilities_sum = [0,0]
        try:
            start = 0
            for line in lines:
                start += 1
                if re.search("Current liabilities",line,re.IGNORECASE):
                    break
            end = 0
            for line in lines:
                end += 1
                if re.search(term_dict["TotalShareholdersEquity"][0],line,re.IGNORECASE):
                    break
            print(start,end,"start & end")
            for line in lines[start:end]:
                if re.search("Accrued",line,re.IGNORECASE):
                    line=line.replace(',', '')
                    line=line.replace('$','')
                    # print(line,"line============================")
                    AccruedLiabilities = re.findall("\(?[0-9.]{1,10}\)?", line)
                    if len(AccruedLiabilities) >= 2:
                        AccruedLiabilities = preprocessing(AccruedLiabilities,balance_sheet_years,unit_used)
                        AccruedLiabilities_sum = [i+j for i,j in zip(AccruedLiabilities,AccruedLiabilities_sum)]
        except Exception as e:
            print(e,"Exception in accrued Fetching")

        ## Accounts recievables

        try:
            start = 0
            for line in lines:
                start += 1
                if re.search("Cash and cash equivalents",line,re.IGNORECASE):
                    break
            end = 0
            for line in lines:
                end += 1
                if re.search(term_dict["TotalShareholdersEquity"][0],line,re.IGNORECASE):
                    break
            print(start,end,"start & end")
            found_account_receivable = False
            found_inventories = False
            found_account_payables = False
            AccountsReceivable = []
            Inventories = []
            AccountsPayable = []
            for line in lines[start:end]:
                if re.search("Accounts receivable",line,re.IGNORECASE):
                    line=line.replace(',', '')
                    line=line.replace('$','')
                    # print(line,"line============================")
                    AccountsReceivable = re.findall("\(?[0-9.]{1,10}\)?", line)
                    if len(AccountsReceivable) >= 2:
                        found_account_receivable = True
                if re.search("Accounts payable",line,re.IGNORECASE):
                    line=line.replace(',', '')
                    line=line.replace('$','')
                    # print(line,"line============================")
                    AccountsPayable = re.findall("\(?[0-9.]{1,10}\)?", line)
                    if len(AccountsPayable) >= 2:
                        found_account_payables = True

                if re.search("Inventories",line,re.IGNORECASE):
                    line=line.replace(',', '')
                    line=line.replace('$','')
                    # print(line,"line============================")
                    Inventories = re.findall("\(?[0-9.]{1,10}\)?", line)
                    if len(Inventories) >= 2:
                        found_inventories = True
                if found_account_payables and found_account_receivable and found_inventories:
                    break

        except Exception as e:
            print(e,"Exception in accounts receivables,payables,inventories")

        AccountsReceivable = preprocessing(AccountsReceivable,balance_sheet_years,unit_used)
        AccountsPayable = preprocessing(AccountsPayable,balance_sheet_years,unit_used)
        Inventories = preprocessing(Inventories,balance_sheet_years,unit_used)

        total_net_found = 0
        for i in total_revenue_patterns:
            for line in lines:#loop through all rows
                if i in line:
                    print("Found",i,line)
                    line=line.replace(',', '')
                    line=line.replace('$','')
                    total_net = re.findall("\S[0-9.,]+\S|\S[0-9]+\S", line)
                    # print(total_net,"totalnet")
                    dict_final['TotalRevenue']=total_net
                    if len(total_net) >= 2:
                        total_net_found = 1

                        break
            if total_net_found:
                break



        list_TR=dict_final.get('TotalRevenue')
        TotalRevenue=preprocessing(list_TR,years,unit_used)
        print(TotalRevenue,"Total Revenue")

        list_COGS=dict_final.get('COGS')
        COGS=preprocessing(list_COGS,years,unit_used)
        COGS = [abs(val) for val in COGS]
        print(COGS,"COGS")




        list_GrossProfit=dict_final.get('GrossProfit')
        GrossProfit=preprocessing(list_GrossProfit,years,unit_used)
        if not any(GrossProfit):
          GrossProfit = [i-j for i, j in zip(map(float,TotalRevenue), map(float,COGS))]
        print(GrossProfit,"GrossProfit")

        list_EBIT=dict_final.get('EBIT')
        EBIT=preprocessing(list_EBIT,years,unit_used)
        print(EBIT,"EBIT")
        if list_EBIT is not None:
          SGA = [i-j for i, j in zip(map(float,GrossProfit), map(float,EBIT))]

        # print(SGA,"SGA")


        if list_EBIT is None:
          list_SGA=dict_final.get('SGA')
          SGA=preprocessing(list_SGA,years,unit_used)
          SGA = [abs(val) for val in SGA]
          EBIT=[i-j for i, j in zip(map(float,GrossProfit), map(float,SGA))]
        print(EBIT,"EBIT")

        if list_EBIT is not None:
          SGA = [i-j for i, j in zip(map(float,GrossProfit), map(float,EBIT))]

        print(SGA,"SGA")

        list_DandA=dict_final.get('DandA')
        DandA=preprocessing(list_DandA,years,unit_used)
        print(DandA,"DandA")
        amort = preprocessing(amort,years,unit_used)

        if len(DandA) == len(amort):
            DandA = [sum(x) for x in zip(DandA, amort)]
        else:
            DandA_updated = []
            for val in DandA:
                val += 0
                DandA_updated.append(val)
            DandA = DandA_updated
        print(DandA,"DandA_Updated")




        list_EBT=dict_final.get('EBT')
        EBT=preprocessing(list_EBT,years,unit_used)
        print(EBT,"EBT")

        if list_EBT is None:
          list_netInterest=dict_final.get('InterestExpense')
          netInterest=preprocessing(list_netInterest,years,unit_used)
          EBT=[i-j for i, j in zip(map(float,EBIT), map(float,netInterest))]
        else:
          netInterest = [i-j for i, j in zip(map(float,EBIT), map(float,EBT))]

        list_netIncome=dict_final.get('NetIncome')
        netIncome=preprocessing(list_netIncome,years,unit_used)
        print(netIncome,"NetINCOME")

        list_Taxes=dict_final.get('Taxes')
        Taxes=preprocessing(list_Taxes,years,unit_used)

        print(Taxes,"Taxes")

        if list_Taxes is None:
          Taxes=[i-j for i, j in zip(map(float,EBT), map(float,netIncome))]
        print(Taxes,"Taxes")

        if list_netIncome is None:
          netIncome=[i-j for i, j in zip(map(float,EBT), map(float,Taxes))]

        otherIncome=[]
        for i in range(len(years)):
          otherIncome.append('0')
        EBT=EBT[:3]
        print(EBT,"EBT")
        print(otherIncome,"otherIncome")

        ############ Balance Sheet Processing Start##########
        print("############ Balance Sheet Processing Start ##########")

        print("balance Sheet Years",balance_sheet_years)


        TotalLiabilitiesAndEquity = dict_final.get('TotalLiabilitiesAndEquity')
        TotalLiabilitiesAndEquity=preprocessing(TotalLiabilitiesAndEquity,balance_sheet_years,unit_used)
        print(TotalLiabilitiesAndEquity,"TotalLiabilitiesAndEquity")

        CashEquivalents = dict_final.get('CashEquivalents')
        CashEquivalents=preprocessing(CashEquivalents,balance_sheet_years,unit_used)
        print(CashEquivalents,"CashEquivalents")

        # AccountsReceivable = dict_final.get('AccountsReceivable')
        # AccountsReceivable=preprocessing(AccountsReceivable,balance_sheet_years,unit_used)
        print(AccountsReceivable,"AccountsReceivable")

        # Inventories = dict_final.get('Inventories')
        # Inventories=preprocessing(Inventories,balance_sheet_years,unit_used)
        print(Inventories,"Inventories")

        TotalCurrentAssets = dict_final.get('TotalCurrentAssets')
        TotalCurrentAssets=preprocessing(TotalCurrentAssets,balance_sheet_years,unit_used)
        print(TotalCurrentAssets,"TotalCurrentAssets")

        PPE = dict_final.get('PPE')
        PPE=preprocessing(PPE,balance_sheet_years,unit_used)
        print(PPE,"PPE")

        Goodwill = dict_final.get('Goodwill')
        Goodwill=preprocessing(Goodwill,balance_sheet_years,unit_used)
        print(Goodwill,"Goodwill")

        IntangibleAssets = dict_final.get('IntangibleAssets')
        IntangibleAssets=preprocessing(IntangibleAssets,balance_sheet_years,unit_used)
        print(IntangibleAssets,"IntangibleAssets")

        TotalAssets = dict_final.get('TotalAssets')
        TotalAssets=preprocessing(TotalAssets,balance_sheet_years,unit_used)
        print(TotalAssets,"TotalAssets")

        CurrentPortionLongTermDebt = dict_final.get('CurrentPortionLongTermDebt')
        CurrentPortionLongTermDebt=preprocessing(CurrentPortionLongTermDebt,balance_sheet_years,unit_used)
        print(CurrentPortionLongTermDebt,"CurrentPortionLongTermDebt")

        # AccountsPayable = dict_final.get('AccountsPayable')
        # AccountsPayable=preprocessing(AccountsPayable,balance_sheet_years,unit_used)
        print(AccountsPayable,"AccountsPayable")

        # AccruedLiabilities = dict_final.get('AccruedLiabilities')
        # AccruedLiabilities=preprocessing(AccruedLiabilities,balance_sheet_years,unit_used)
        # print(AccruedLiabilities,"AccruedLiabilities")

        TotalCurrentLiabilities = dict_final.get('TotalCurrentLiabilities')
        TotalCurrentLiabilities=preprocessing(TotalCurrentLiabilities,balance_sheet_years,unit_used)
        print(TotalCurrentLiabilities,"TotalCurrentLiabilities")

        LongTermDebt = dict_final.get('LongTermDebt')
        LongTermDebt=preprocessing(LongTermDebt,balance_sheet_years,unit_used)
        print(LongTermDebt,"LongTermDebt")

        TotalLiabilities = dict_final.get('TotalLiabilities')
        TotalLiabilities=preprocessing(TotalLiabilities,balance_sheet_years,unit_used)
        print(TotalLiabilities,"TotalLiabilities")



        TotalShareholdersEquity = dict_final.get('TotalShareholdersEquity')
        TotalShareholdersEquity=preprocessing(TotalShareholdersEquity,balance_sheet_years,unit_used)
        print(TotalShareholdersEquity,"TotalShareholdersEquity")


        if all(TotalLiability == 0 for TotalLiability in TotalLiabilities):
            TotalLiabilities = [i-j for i,j in zip(TotalLiabilitiesAndEquity,TotalShareholdersEquity)]
            print("Derived TotalLiabilities",TotalLiabilities)

        OtherCurrentLiabilities = []
        OtherCurrentAssets = []
        OtherAssets = []
        OtherLiabilities = []
        for i in range(len(TotalCurrentAssets)):
            temp_val1 = TotalCurrentAssets[i] - (CashEquivalents[i] + AccountsReceivable[i] + Inventories[i])
            OtherCurrentAssets.append(temp_val1)

            temp_val2 = TotalAssets[i] - (PPE[i] + IntangibleAssets[i] + Goodwill[i]+TotalCurrentAssets[i])
            OtherAssets.append(temp_val2)

            temp_val3 = TotalCurrentLiabilities[i] - (CurrentPortionLongTermDebt[i] + AccountsPayable[i] + AccruedLiabilities_sum[i])
            OtherCurrentLiabilities.append(temp_val3)

            temp_val4 = TotalLiabilities[i] - LongTermDebt[i]
            OtherLiabilities.append(temp_val4) 

        print(OtherCurrentAssets,"OtherCurrentAssets")
        print(OtherAssets,"OtherAssets")
        print(OtherCurrentLiabilities,"OtherCurrentLiabilities")
        print(OtherLiabilities,"OtherLiabilities")
        print(AccruedLiabilities_sum,"AccruedLiabilities")


        print("############ Balance Sheet Processing End ##########")
        ############ Balance Sheet Processing End ##########

        years_in_ascending = years[:]
        years_in_ascending.sort(reverse=True)

        if years != years_in_ascending:
            years = years [::-1]
            EBT = EBT[::-1]
            otherIncome = otherIncome[::-1]
            TotalRevenue = TotalRevenue[::-1]
            COGS = COGS[::-1]
            SGA = SGA[::-1]
            DandA = DandA[::-1]
            netInterest = netInterest[::-1]
            Taxes = Taxes[::-1]
            GrossProfit = GrossProfit[::-1]
            EBIT = EBIT[::-1]
            netIncome = netIncome[::-1]


        created_on = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # try:
        connection = mysql.connector.connect(host="35.225.71.54",
                                                database='finance',
                                                user='investor',
                                                password='investor')
        if connection.is_connected():
          db_Info = connection.get_server_info()
          print("Connected to MySQL Server version ", db_Info)
          cursor = connection.cursor()

        projections = 4  # hardcodedd
        print(Company,"company")
        query = "insert into company_master (companyname,company,period,actuals,projections,createdby,createdon,filename,industry,statementtype)" \
                "values ('" + company_name + "','" + Company + "','" + period + "'," + str(len(years)) + "," + str(projections) + ",'" + user + "','" + created_on + "','" + filename + "','" + industry + "','" + statement_type + "')"

        cursor.execute(query)
        # connection.commit()
        for i in range(len(years)):
          latest_value = years_association[years[i]]
          ebitda = EBIT[i] + DandA[i]
          if all(v == 0 for v in TotalRevenue):
            grossprofitmargin=0
            ebitmargin=0
            ebitdamargin=0
            ebtmargin=0
            netincomemargin=0
          else:
            try:
              grossprofitmargin = float((GrossProfit[i] / TotalRevenue[i]) * 100)      
              ebitmargin = float((EBIT[i] / TotalRevenue[i]) * 100)
              ebitdamargin = float((ebitda/ TotalRevenue[i]) * 100)
              print("ebitdamargin",ebitdamargin)
              ebtmargin = float((EBT[i] / TotalRevenue[i]) * 100)
              print("ebtmargin",ebtmargin)
              netincomemargin = float((netIncome[i] /TotalRevenue[i]) * 100)
            except Exception as e:
              print("exception margin values")
          if len(years)-1 != i:
              try:
                  revenuepercent = ((TotalRevenue[i]-TotalRevenue[i+1])/TotalRevenue[i+1])*100
                  #revenuepercent=[0,0,0]
                  # print("revenuepercent",revenuepercent)
                  cogspercent = (COGS[i]/TotalRevenue[i])*100
                  # print("cogspercent",cogspercent)
                  sgapercent = (SGA[i]/TotalRevenue[i])*100
                  # print("sgapercent",sgapercent)
                  dapercent = (DandA[i]/TotalRevenue[i])*100
                  # print("dapercent",dapercent)

              except:
                  revenuepercent=0
                  cogspercent=0
                  sgapercent=0
                  dapercent=0
                  print("excpetion in Total Revenue Percenetage")
          else:
              revenuepercent=0
              cogspercent=0
              sgapercent=0
              dapercent=0

          print("Query================")
          query = "insert into company_actuals (companyname,asof,latest,totalrevenue,cogs,sga,da,netinterest,otherincome," \
                  "taxes,grossprofit,ebit,ebitda,netincome,grossprofitmargin,ebitmargin,ebitdamargin,ebtmargin,netincomemargin,ebt,revenuepercent,cogspercent,sgapercent,dapercent) values(" \
                  "'" + company_name + "'," +str(years[i]) + "," + str(
                      latest_value) + "," + str(TotalRevenue[i]) + "," + str(COGS[i]) + "," + str(SGA[i]) + "," + str(
                      DandA[i]) + "," + str(netInterest[i]) + "," + str(otherIncome[i]) + "," + str(abs(Taxes[i])) + "," + str(
                      GrossProfit[i]) + "," + str(EBIT[i]) + "," + str(ebitda) + "," + str(netIncome[i]) + "," + str(
                      grossprofitmargin) + "," + str(ebitmargin) + "," + str(ebitdamargin) + "," + str(
                      ebtmargin) + "," + str(netincomemargin) + "," + str(EBT[i]) + "," + str(revenuepercent) + "," + str(cogspercent) + "," + str(sgapercent) + "," + str(dapercent) +")"  
          cursor.execute(query)
          connection.commit()  # save records
    except Exception as e:
        print("Error in Program execution", e)
        message = "Fail"

    return message

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)
    print("File {} uploaded to {}.".format(source_file_name, destination_blob_name))
    return "File {} uploaded to {}.".format(source_file_name, destination_blob_name)


if __name__ == "__main__":

    company_name = sys.argv[1]

    file_path = '/home/srinidhi/angular/ExtractedFiles/'+company_name+".pdf"
    destination_path = company_name+'/'+company_name+".pdf"
    upload_blob('sample_pdf', file_path, destination_path)
    
    file_path = 'gs://sample_pdf/'+company_name+'/'+company_name+'.pdf'
    model_name = 'projects/410058770032/locations/us-central1/models/TEN4430858137100091392'
    period = "Y"
    user = 'admin'
    industry = 'communications'
    statement_type = 'all statements'
    filename = company_name + ".pdf"
    

    result = main_function(file_path,model_name,company_name,period,user,industry,statement_type,filename)

    print(result)

