import os
import pymysql.cursors
import time 
import pathlib
import queue
import sys
import threading
import json

import docker  # https://pypi.org/project/docker

#############################################################################################################################################

DOCKER_IMAGE = "ubuntu-judge"

#############################################################################################################################################

from flask import *
app = Flask(__name__)

def set_secret_key():
    f = open("secret_key.json", "r")
    s_key = json.load(f)
    print(s_key)
    app.secret_key = s_key["app"]


#############################################################################################################################################

def get_recorde_num(connection=None, table=None):
    with connection.cursor() as cursor:   
        sql = "select count(*) from " + table;
        cursor.execute(sql)
        results = cursor.fetchall()
        return int(results[0]["count(*)"]) + 1
    return 1




#############################################################################################################################################
##
## PROBLEMS
##
#############################################################################################################################################
#############################################################################################################################################

@app.route("/problem/<problem_id>")
def problem(problem_id=None):
    return render_template("problem.html", username=session['username'], problem_id=problem_id)


    

#############################################################################################################################################
##
## SUBMIT
##
#############################################################################################################################################
#############################################################################################################################################

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

#############################################################################################################################################
@app.route("/problem/<problem_id>/submit", methods=["GET", "POST"])
def submit(problem_id=None):
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == "GET":
        return render_template("submit.html", error="", username=session['username'], problem_id=problem_id)
 
    lang = request.form["lang-sel"]
    user = session['username']
    code = request.form["source_code"] 

    if code == "":
        return render_template("submit.html", error="Source Code is empty!", user=user, username=session['username'], problem_id=problem_id)

    # Compile and run seed1 with Docker.
    exit_code, stdout, stderr = docker_exec_submit(code=code, lang=lang)
    stdout = stdout.decode("utf8") if stdout is not None else ""
    stderr = stderr.decode("utf8") if stderr is not None else ""
    
    # Compile Error
    if exit_code: 
        return render_template("submit.html", error="Compile Error!\n" + str(stderr), code=code, user=user, username=session['username'], problem_id=problem_id)

    
    # Connect to MySQL.
    connection = pymysql.connect(
        host        = "localhost",
        user        = "root",
        password    = "root",
        db          = "endless_marathon",
        charset     = "utf8",
        cursorclass = pymysql.cursors.DictCursor)
    
    
    # Register the submission.
    ###################################################################
    submission_id = get_recorde_num(connection=connection, table="submissions")
    user_id       = session['username']
    language_id   = 1 # Not defined
    time_stamp    = time.strftime('%Y-%m-%d %H:%M:%S')
    
    # user_name to user_id
    with connection.cursor() as cursor:   
        sql = "select id from users where name='" + user_id + "'"
        cursor.execute(sql)
        user_id = cursor.fetchall()[0]['id']

    with connection.cursor() as cursor:
        sql = '''INSERT INTO submissions (id, user_id, problem_id, language_id, code, created_at) VALUES (%s, %s, %s, %s, %s, %s)'''
        r = cursor.execute(sql, (submission_id, user_id, problem_id, language_id, code, time_stamp))
        connection.commit()
    
    
    # Register the result.
    ###################################################################
    submission_result_id = get_recorde_num(connection=connection, table="submission_results")
    score = float(stdout.split(' ')[2])
    execution_time = 0 # Not defined

    with connection.cursor() as cursor:
        sql = '''INSERT INTO submission_results (id, submission_id, execution_time, score, created_at) VALUES (%s, %s, %s, %s, %s)'''
        r = cursor.execute(sql, (submission_result_id, submission_id, execution_time, score, time_stamp))
        connection.commit()
        
        
    connection.close()
    return render_template("submission_success.html", username=session['username'], problem_id=problem_id)





#############################################################################################################################################
##
## SUBMITTIONS
##
#############################################################################################################################################
#############################################################################################################################################

@app.route("/problem/<problem_id>/submissions")
def submissions(problem_id=None):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Connect to MySQL.
    connection = pymysql.connect(
        host        = "localhost",
        user        = "root",
        password    = "root",
        db          = "endless_marathon",
        charset     = "utf8",
        cursorclass = pymysql.cursors.DictCursor)
    
    user_id = session['username']
    
    # user_name to user_id
    with connection.cursor() as cursor:   
        sql = "select id from users where name='" + user_id + "'"
        cursor.execute(sql)
        user_id = cursor.fetchall()[0]['id']

    # Get Submission Information.
    result = ""
    with connection.cursor() as cursor:
        sql = '''
        SELECT
            submission_results.submission_id AS submission_id,
            users.name AS user_name,
            languages.name AS language,
            submission_results.score AS score,
            submission_results.execution_time AS time,
            submissions.created_at AS date
        FROM
            submission_results,
            submissions,
            users,
            languages,
            problems
        WHERE
            submission_results.submission_id = submissions.id AND
            submissions.user_id = users.id AND
            submissions.language_id = languages.id AND
            problems.id = ''' + str(problem_id) + ''' AND
            users.id = ''' + str(user_id)
        cursor.execute(sql)
        result = cursor.fetchall()
        
    connection.close()
    
    return render_template("submissions.html", submits=result, username=session['username'], problem_id=problem_id)
    
#############################################################################################################################################
@app.route("/show_code", methods=["GET", "POST"])
def show_code():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == "GET":
        return render_template("submissions.html", username=session['username'], problem_id=request.form["problem_id"])
    
    # Connect to MySQL.
    connection = pymysql.connect(
        host        = "localhost",
        user        = "root",
        password    = "root",
        db          = "endless_marathon",
        charset     = "utf8",
        cursorclass = pymysql.cursors.DictCursor)

    # Get Submission Information.
    result = ""
    with connection.cursor() as cursor:   
        sql = "select * from submissions where id=" + str(request.form["submission_id"]);
        cursor.execute(sql)
        result = cursor.fetchall()[0]
        
    connection.close()
    line_count = (result["code"].count(os.linesep) + 2) * 1.3
    return render_template("show_code.html", code=result["code"], submit=result, line=line_count, username=session['username'], problem_id=request.form["problem_id"])
    
    
    
    
    
#############################################################################################################################################
##
## CODE TEST
##
#############################################################################################################################################
#############################################################################################################################################

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

#############################################################################################################################################
@app.route("/problem/<problem_id>/code_test", methods=["GET", "POST"])
def code_test(problem_id=None):
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == "GET":
        return render_template("code_test.html", code="", stdin="", stdout="", stderr="", username=session['username'], problem_id=problem_id)
    
    code  = request.form["code"] if "code" in request.form else ""
    stdin = request.form["stdin"] if "stdin" in request.form else ""
    lang  = request.form["lang-sel"]

    exit_code, stdout, stderr = docker_exec_code_test(code, lang, stdin)
    return render_template("code_test.html", code=code, stdin=stdin, stdout=stdout, stderr=stderr, username=session['username'], problem_id=problem_id)






#############################################################################################################################################
##
## STANDINGS
##
#############################################################################################################################################
#############################################################################################################################################

@app.route("/problem/<problem_id>/standings")
def standings(problem_id=None):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Connect to MySQL.
    connection = pymysql.connect(
        host        = "localhost",
        user        = "root",
        password    = "root",
        db          = "endless_marathon",
        charset     = "utf8",
        cursorclass = pymysql.cursors.DictCursor)
    
    # Get Standings Information.
    standing = ""
    with connection.cursor() as cursor:
        sql = '''
        SELECT
            result.user_name,
            result.language,
            MAX(result.score) AS score,
            result.time
        FROM (
            SELECT
                submission_results.submission_id AS submission_id,
                submissions.problem_id AS problem_id,
                problems.name AS problem_name,
                users.name AS user_name,
                languages.name AS language,
                submission_results.score AS score,
                submission_results.execution_time AS time,
                submissions.created_at AS date
            FROM
                submission_results,
                submissions,
                users,
                languages,
                problems
            WHERE
                submission_results.submission_id = submissions.id AND
                submissions.user_id = users.id AND
                submissions.language_id = languages.id AND
                submissions.problem_id = problems.id AND
                problems.id = %s
        ) AS result
        GROUP BY
            result.user_name,
            result.language,
            result.time
        '''
        cursor.execute(sql, (int(problem_id)))
        standing = cursor.fetchall()
        
    connection.close()
    
    return render_template("standings.html", standing=standing, problem_id=problem_id, username=session['username'])
    



#############################################################################################################################################
##
## LOGIN & LOGOUT
##
#############################################################################################################################################
#############################################################################################################################################

@app.route("/logout", methods=["GET", "POST"])
def logout():
    if 'username' not in session:
        return redirect(url_for('login'))
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route("/login", methods=["GET", "POST"])
def login():
    if 'username' in session:
        return redirect(url_for('index'))

    if request.method == "POST":
        connection = pymysql.connect(
            host        = "localhost",
            user        = "root",
            password    = "root",
            db          = "endless_marathon",
            charset     = "utf8",
            cursorclass = pymysql.cursors.DictCursor)

        username = request.form['username']
        password = request.form['password']
        with connection.cursor() as cursor:   
            sql = "select count(name) from users where name='" + username + "'";
            cursor.execute(sql)
            result = int(cursor.fetchall()[0]["count(name)"])
            if result == 0:
                connection.close()
                return render_template("login.html", error_login="Who are you?")

        correct_pass = ""
        with connection.cursor() as cursor:   
            sql = "select * from users where name='" + username + "'";
            cursor.execute(sql)
            correct_pass = cursor.fetchall()[0]["secret_value"]
 
        if password != correct_pass:
            return render_template("login.html", error_login="Your password is incorrect.")

        session['username'] = username 
        return redirect(url_for('index'))

    return render_template("login.html")
    

    
    
    
#############################################################################################################################################
##
## SIGN UP
##
#############################################################################################################################################
#############################################################################################################################################

@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    if 'username' in session:
        return redirect(url_for('index'))
    if request.method == "GET":
        return render_template("sign_up.html", username=session['username'])
    else:
        user_id  = request.form["userid"]
        password = request.form["password"]
        if (user_id == ""):
            return render_template("login.html", error_sign_up="User ID is empty!")
        if (password  == ""):
            return render_template("login.html", error_sign_up="Password is empty!")
        
        connection = pymysql.connect(
            host        = "localhost",
            user        = "root",
            password    = "root",
            db          = "endless_marathon",
            charset     = "utf8",
            cursorclass = pymysql.cursors.DictCursor)

        with connection.cursor() as cursor:   
            sql = "select count(name) from users where name='" + user_id + "'";
            cursor.execute(sql)
            result = int(cursor.fetchall()[0]["count(name)"])
            if result != 0:
                connection.close()
                return render_template("login.html", error_sign_up="Already Exists " + user_id)

        user_num = get_recorde_num(connection=connection, table="users")
        time_stamp = time.strftime('%Y-%m-%d %H:%M:%S')
        with connection.cursor() as cursor:   
            sql = '''INSERT INTO users (id, name, secret_value, created_at) VALUES (%s, %s, %s, %s)'''
            r = cursor.execute(sql, (user_num, user_id, password, time_stamp))
            connection.commit()
        connection.close()

    return render_template("login.html", error_sign_up="Success!")





#############################################################################################################################################
##
## INDEX
##
#############################################################################################################################################
#############################################################################################################################################

@app.route("/")
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Connect to MySQL.
    connection = pymysql.connect(
        host        = "localhost",
        user        = "root",
        password    = "root",
        db          = "endless_marathon",
        charset     = "utf8",
        cursorclass = pymysql.cursors.DictCursor)
    
    # Get problem information.
    problems = ""
    with connection.cursor() as cursor:   
        sql = "select * from problems" 
        cursor.execute(sql)
        problems = cursor.fetchall()
    
    return render_template("index.html", username=session['username'], problems=problems)

if __name__ == "__main__":
    set_secret_key()
    app.run(host="localhost", port=5000)


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    