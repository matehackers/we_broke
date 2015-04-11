from bottle import route, run, template
import fetch_balance

@route('/balance')
def index():
    return template('{ balance: {{balance}}}', balance=fetch_balance.balance)

run(host='localhost', port=8090)
