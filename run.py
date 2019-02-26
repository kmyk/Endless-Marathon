from flask import *
app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/code_test', methods=["GET", "POST"])
def code_test():
    if request.method == "GET":
        return render_template('code_test.html')
    else:
        return render_template('code_test.html')
    
if __name__ == '__main__':
	app.run()


