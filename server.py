from bottle import route, run, template
import balance

@route('/balance')
def index():
    return balance.fetch()

run(host='localhost', port=8090)
