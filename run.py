import os
import pymysql.cursors
import time 
import pathlib
import queue
import sys
import threading

import docker  # https://pypi.org/project/docker

##################################################################################################################

DOCKER_IMAGE = "ubuntu-judge"

##################################################################################################################

from flask import *
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

##################################################################################################################
def docker_exec_code_test(code=None, lang=None, stdin=None):
    problem_dir = "problems/execute"
    if not os.path.exists(problem_dir):
        os.makedirs(problem_dir)

    with open(problem_dir + "/input.txt", "w") as file:
        file.write(stdin)

    cmd = ""
    if lang == "cpp":
        cmd = "bash -c 'g++ a.cpp -o a.out -std=c++11 && time ./a.out < input.txt'"
        with open(problem_dir + "/a.cpp", "w") as file:
            file.write(code)
    elif lang == "java":
        cmd = "bash -c 'javac Main.java && time java Main < input.txt'"
        with open(problem_dir + "/Main.java", "w") as file:
            file.write(code)

    ############################################
    client = docker.from_env()
    working_dir = '/mnt/workspace'
    volumes = { str(pathlib.Path.cwd()) + "/" + problem_dir: { 'bind': working_dir, 'mode': 'rw' } }

    que = queue.Queue()
    try:
        container = client.containers.run(
            image=DOCKER_IMAGE,
            detach=True,
            stdin_open=True,
            volumes=volumes,
            working_dir=working_dir,
            network_disabled=True)

        def func():
            que.put(container.exec_run(cmd, demux=True))
        thread = threading.Thread(target=func)
        thread.start()
        thread.join(timeout=30)
    finally:
        container.kill()
        container.remove()

    exit_code, (stdout, stderr) = que.get()
    stdout = stdout.decode("utf8") if stdout is not None else ""
    stderr = stderr.decode("utf8") if stderr is not None else ""
    return exit_code, stdout, stderr

###################
@app.route("/code_test", methods=["GET", "POST"])
def code_test():
    if request.method == "GET":
        return render_template("code_test.html", code="", stdin="", stdout="", stderr="")
    else:
        code  = request.form["code"] if "code" in request.form else ""
        stdin = request.form["stdin"] if "stdin" in request.form else ""
        lang  = request.form["lang-sel"]

        exit_code, stdout, stderr = docker_exec_code_test(code, lang, stdin)
        return render_template("code_test.html", code=code, stdin=stdin, stdout=stdout, stderr=stderr)

    
##################################################################################################################
def docker_exec_submit(code=None, lang=None):
    problem_dir = "problems/traveling-salesman"
    cmd = ""
    if lang == "cpp":
        cmd = "bash -c 'g++ a.cpp -std=c++11 -o a.out && java -jar Tester.jar -exec ./a.out -seed 1'"
        with open(problem_dir + "/a.cpp", "w") as file:
            file.write(code)
    elif lang == "java":
        cmd = '''bash -c "javac Main.java && java -jar Tester.jar -exec 'java Main' -seed 1"'''
        with open(problem_dir + "/Main.java", "w") as file:
            file.write(code)

    client = docker.from_env()

    working_dir = '/mnt/workspace'
    volumes = { str(pathlib.Path.cwd()) + "/" + problem_dir: { 'bind': working_dir, 'mode': 'rw' } }

    que = queue.Queue()
    try:
        container = client.containers.run(
            image=DOCKER_IMAGE, 
            detach=True, 
            stdin_open=True, 
            volumes=volumes, 
            working_dir=working_dir, 
            network_disabled=True)
        def func():
            que.put(container.exec_run(cmd, demux=True))
        thread = threading.Thread(target=func)
        thread.start()
        thread.join(timeout=30)
    finally:
        container.kill()
        container.remove()

    exit_code, (stdout, stderr) = que.get()
    return exit_code, stdout, stderr

#################
def get_recorde_num(connection=None, table=None):
    with connection.cursor() as cursor:   
        sql = "select count(*) from " + table;
        cursor.execute(sql)
        results = cursor.fetchall()
        return int(results[0]["count(*)"]) + 1
    return 1

#################
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
            return render_template("submit.html", error="UserID is empty!", code=code)
        if code == "":
            return render_template("submit.html", error="Source Code is empty!", user=user)
        
        exit_code, stdout, stderr = docker_exec_submit(code=code, lang=lang)
        stdout = stdout.decode("utf8") if stdout is not None else ""
        stderr = stderr.decode("utf8") if stderr is not None else ""
        if exit_code:
            return render_template("submit.html", error="Compile Error!\n" + str(stderr), code=code, user=user)

        ############  
        code_length = 0
        time_stamp = time.strftime('%Y-%m-%d %H:%M:%S')
        st = stdout.split(' ')
        score = float(st[2])
        execution_time = 0

        connection = pymysql.connect(
            host        = "localhost",
            user        = "root",
            password    = "",
            db          = "endless_marathon",
            charset     = "utf8",
            cursorclass = pymysql.cursors.DictCursor)

        #### 
        code_id = get_recorde_num(connection=connection, table="submissions")
        
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

        line_count = (result["code"].count(os.linesep) + 2) * 1.3
        return render_template("show_code.html", code=result["code"], submit=result, line=line_count)
    
# problems
##################################################################################################################
@app.route("/problems/traveling_salesman")
def traveling_salesman():
    return render_template("problems/traveling_salesman.html")

##################################################################################################################
if __name__ == "__main__":
    app.run(host="localhost", port=5000)


