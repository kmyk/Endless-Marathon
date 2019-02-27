import os
import subprocess
import pymysql.cursors
import time 

from flask import *
app = Flask(__name__)

@app.route("/")
def index():
	return render_template("index.html")

##################################################################################################################
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

    
##################################################################################################################
@app.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "GET":
        return render_template("submit.html", error="")
    else:
        lang = request.form["lang-sel"]
        prob = request.form["prob-sel"]
        user = request.form["userid"]
        code = request.form["source_code"] 
            
        if user == "":
            return render_template("submit.html", error="UserID is empty!")
        if code == "":
            return render_template("submit.html", error="Source Code is empty!")
        
        if lang == "cpp":
            try:
                if not os.path.exists("execute"):
                    os.makedirs("execute")
                with open("execute/a.cpp", "w") as file:
                    file.write(code)
                cmd = "g++ execute/a.cpp -std=c++11 -o execute/a.out"
                ret = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
            except subprocess.CalledProcessError as e:   
                return render_template("submit.html", error="Compile Error! " + str(e.output))
  
        code_length = 0
        time_stamp = time.strftime('%Y-%m-%d %H:%M:%S')
        score = 0
        execution_time = 0

        ############
        connection = pymysql.connect(
            host        = "localhost",
            user        = "root",
            password    = "",
            db          = "endless_marathon",
            charset     = "utf8",
            cursorclass = pymysql.cursors.DictCursor)

        # submit id
        code_id = ""
        with connection.cursor() as cursor:   
            sql = "select count(code_id) from submissions";
            cursor.execute(sql)
            results = cursor.fetchall()
            code_id = int(results[0]["count(code_id)"]) + 1
        
        with connection.cursor() as cursor:
            sql = '''INSERT INTO submissions (
                code_id, 
                user_id, 
                problem_id, 
                language, 
                code,
                code_length,
                execution_time,
                score,
                time_stamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
            r = cursor.execute(sql, (
                code_id, 
                user, 
                prob, 
                lang, 
                code,
                code_length,
                execution_time,
                score,
                time_stamp))
            connection.commit()
        connection.close()

        return '''
            <!DOCTYPE html>
            <html>
                <head>
                    <meta charset="utf-8">
                    <meta name="author" content="kosakkun">
                    <meta name="description" content="">
                    <title>Endless Marathon</title>
                </head>
                <body>
                    Success! : <a href="/submit">Submit</a>
                </body>
            </html>'''

##################################################################################################################
@app.route("/submissions", methods=["GET", "POST"])
def submissions():
    if request.method == "GET":
        return render_template("submissions.html")
    else:
        user = request.form["userid"]
        if user == "":
            return render_template("submissions.html", error="UsedID is empty")

        connection = pymysql.connect(
            host        = "localhost",
            user        = "root",
            password    = "",
            db          = "endless_marathon",
            charset     = "utf8",
            cursorclass = pymysql.cursors.DictCursor)
        
        results = ""
        with connection.cursor() as cursor:   
            sql = "select * from submissions where user_id=%s";
            cursor.execute(sql, (user))
            results = cursor.fetchall()
        connection.close()

        return render_template("submissions.html", submits=results)
    
    
##################################################################################################################
@app.route("/show_code", methods=["GET", "POST"])
def show_code():
    if request.method == "GET":
        return render_template("submissions.html")
    else:
        connection = pymysql.connect(
            host        = "localhost",
            user        = "root",
            password    = "",
            db          = "endless_marathon",
            charset     = "utf8",
            cursorclass = pymysql.cursors.DictCursor)

        result = ""
        with connection.cursor() as cursor:   
            sql = "select * from submissions where code_id=%s";
            cursor.execute(sql, (request.form["code_id"]))
            result = cursor.fetchall()[0]
        connection.close()

        line_count = result["code"].count(os.linesep) + 2
        return render_template("show_code.html", code=result["code"], submit=result, line=line_count)

##################################################################################################################
if __name__ == "__main__":
	app.run(host="localhost", port=5000)


