import os
import subprocess

from flask import *
app = Flask(__name__)

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/code_test", methods=["GET", "POST"])
def code_test():
    if request.method == "GET":
        return render_template("code_test.html", code="", stdin="", stdout="", stderr="")
    else:
        code  = request.form["code"] if "code" in request.form else ""
        stdin = request.form["stdin"] if "stdin" in request.form else ""
        lang  = request.form["lang-sel"]
        
        if not os.path.exists("execute"):
            os.makedirs("execute")
        with open("execute/input.txt", "w") as file:
            file.write(stdin)
        
        stdout = ""
        stderr = ""
        if lang == "cpp":
            with open("execute/a.cpp", "w") as file:
                file.write(code)
            cmd = "g++ execute/a.cpp -o execute/a.out -std=c++11 && time execute/a.out < execute/input.txt"
            proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout = proc.stdout.decode("utf8")
            stderr = proc.stderr.decode("utf8")
        
        return render_template("code_test.html", code=code, stdin=stdin, stdout=stdout, stderr=stderr)

if __name__ == "__main__":
	app.run(host="localhost", port=5000)


