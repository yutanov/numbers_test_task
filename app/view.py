from flask import Flask
from flask import render_template
from db import session, Orders

app = Flask(__name__)

s = session()

@app.route('/')
def index():
    data_list = s.query(Orders).order_by(Orders.id).all()
    return render_template('index.html', data_list=data_list)


if __name__ == '__main__':
    app.run()
