import requests
import requests
import pygsheets
import gspread
import subprocess
from xml.etree import ElementTree
from auth import spreadsheet_service
from auth import drive_service
from oauth2client.service_account import ServiceAccountCredentials

# Endpoint
url_kurs_nbp = "https://api.nbp.pl/api/exchangerates/rates"
url_nr_word_pl = "https://api.officeblog.pl/slownie.php?format=3&kwota="
url_nr_word_en = "https://api.officeblog.pl/inwords.php?format=3&amount="


# A GET request to the API NBP exchange of the day
def exchange_rate(data):
    response_nbp = requests.get(url_kurs_nbp +'/a/eur/' + data + '?format=json')
    data_nbp = response_nbp.json()
    kurs = data_nbp['rates'][0]['mid']
    kurs_table_id = data_nbp['rates'][0]['no']
    return kurs, kurs_table_id

# Calculos and number to word pl and en
def calculos_amount_in_word(hours, rate):
    working_hours = int(hours)
    rate= int(rate)
    workingdays = working_hours/8
    amount = workingdays*rate
    amount_str = str(round(amount,2))
    amount_zl = rate*amount
    amount_zl = str(amount_zl)
 
    response_nr_word_pl = requests.get(url_nr_word_pl + str(amount_str))
    nr_word_pl = response_nr_word_pl.text.strip()
    nr_word_pl = nr_word_pl.replace("złotych","")
    nr_word_pl = nr_word_pl.replace("gr","")

    response_nr_word_en = requests.get(url_nr_word_en + str(amount_str))
    nr_word_en = response_nr_word_en.text.strip()
    nr_word_en = nr_word_en.replace("zlotys", "")
    return nr_word_pl.upper(), nr_word_en.upper(), amount_str, amount_zl, working_hours, workingdays

# Upload gSheet FV template on gDrive and download a pdf
def create_fv(nr_word_pl, nr_word_en, working_hrs, working_days, fv_issue_date, kurs_table_id, rate_exchange, date_exchng, seller, buyer):
    #Create scope
    scope =  ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

    #authorization
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scopes=scope)
    file = gspread.authorize(creds)

    #open spreadsheet
    spreadsheet_template = 'Invoice_template'
    spreadsheet_name = 'Invoice_MONTH'
    workbook = file.open(spreadsheet_template)
    sheet = workbook.sheet1

    #fillin the gSheet
    sheet.update_acell('G2',str(fv_issue_date))
    sheet.update_acell('C31',str(nr_word_pl) +'\n'+ str(nr_word_en))
    sheet.update_acell('D25',str(working_days) +'\n'+ '('+str(working_hrs)+'h/8)')
    sheet.update_acell('F25','='+ str(working_days) +'*E25')
    sheet.update_acell('E33',str(date_exchng))
    sheet.update_acell('F33',str(kurs_table_id))
    sheet.update_acell('G33',str(rate_exchange))
    sheet.update_acell('A9',str(seller))
    sheet.update_acell('F9',str(buyer))


    # Download Spreadsheet as PDF file.
    url = 'https://docs.google.com/spreadsheets/export?format=pdf&id=' + str(workbook.id)
    print(url)
    headers = {'Authorization': 'Bearer ' + creds.create_delegated("").get_access_token().access_token}
    res = requests.get(url, headers=headers)
    with open(spreadsheet_name + ".pdf", 'wb') as f:
        f.write(res.content)

    #Open downloaded PDF
    subprocess.Popen(["open", spreadsheet_name + ".pdf"])
   


   

