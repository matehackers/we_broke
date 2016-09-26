from bottle import route, run, template
import balance

@route('/balance')
def index():
    return balance.fetch()

run(host='0.0.0.0', port=8090)
