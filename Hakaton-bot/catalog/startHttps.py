from flask import Flask, render_template

import ssl

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/auth')
def auth():
    return render_template('auth.html')

@app.route('/reg')
def reg():
    return render_template('reg.html')

@app.route('/market')
def market():
    return render_template('market.html')

if __name__ == '__main__':  
     app.run(host='127.0.0.1',debug=True, ssl_context='adhoc')