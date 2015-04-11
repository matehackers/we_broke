from bottle import route, run, template
import fetch_balance

@route('/balance')
def index():
    return { 'balance': fetch_balance.refresh() }

run(host='localhost', port=8090)
