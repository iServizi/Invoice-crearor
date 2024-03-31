from flask import Flask, render_template, request
#from weather import get_current_weather
from waitress import serve
from nbpapi_flask import calculos_amount_in_word, exchange_rate, create_fv

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
        return render_template('index.html')

@app.route('/inputdata')
def display_values():
        hours = request.args.get('workinghours') 
        rate = request.args.get('rate')
        data_exchange = request.args.get('data_rate')

        print(hours)
        print(data_exchange)
        print(rate)

        amount_in_word_pl = calculos_amount_in_word(hours, rate)[0]
        amount_in_word_en = calculos_amount_in_word(hours, rate)[1] 
        amount = calculos_amount_in_word(hours, rate)[2] 
        workingdays = calculos_amount_in_word(hours, rate)[5] 
        #amount_zl = calculos_amount_in_word(hours, rate)[3] 

        rate_exchange = exchange_rate(data_exchange)[0]
        kurs_table_id = exchange_rate(data_exchange)[1]
        print(rate_exchange)

        #return amount_in_word + str(rate_exchange)
        return render_template('calculation.html', 
                               amount_en = str(amount_in_word_en), 
                               amount_pl = str(amount_in_word_pl), 
                               amount_nr=str(amount), 
                               rate_exchange = rate_exchange,
                               kurs_tableid = kurs_table_id,
                               working_hrs = hours,
                               working_days = workingdays,
                               date_exchng = data_exchange)
                               #amount_zl = amount_zl)
@app.route('/fillingsheet')
def fillin_gsheet():
        amount_en = request.args.get('amount_en') 
        amount_pl = request.args.get('amount_pl')
        fv_issue_date = request.args.get('fv_issue_date')
        working_hrs = request.args.get('working_hrs')
        working_days = request.args.get('working_days')
        kurs_table_id = request.args.get('kurs_tableid')
        rate_exchange = request.args.get('rate_exchange')
        date_exchng = request.args.get('date_exchng')
        seller = request.args.get('seller')
        buyer = request.args.get('buyer')

        create_fv(amount_en, amount_pl, working_hrs,working_days, fv_issue_date,kurs_table_id, rate_exchange,date_exchng, seller, buyer)
        
        return "...DONE"
 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

   