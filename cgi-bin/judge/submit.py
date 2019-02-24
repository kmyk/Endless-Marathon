#!/usr/bin/env python3

import cgi
form = cgi.FieldStorage()

lang = form["lang-sel"].value
prob = form["prob-sel"].value
code = ""

if "source_code" in form:
    code = form["source_code"]
else:
    print("Content-Type: text/html\n")
    print('''
    <!DOCTYPE html>
    <html>
        <head>
            <meta charset="utf-8">
            <meta name="author" content="kosakkun">
            <meta name="description" content="">
            <title>Endless Marathon</title>
        </head>
        <body>
            Failed! Code is empty : <a href="/submit.html">Submit</a>
        </body>
    </html>
    ''')
    exit(0)


# insert submission
#####################################################################################
import pymysql.cursors

connection = pymysql.connect(
    host        = "localhost",
    user        = "root",
    password    = "",
    db          = "submit",
    charset     = "utf8",
    cursorclass = pymysql.cursors.DictCursor)

# submit id
CodeID = ""
with connection.cursor() as cursor:   
    sql = "select count(CodeID) from code3";
    cursor.execute(sql)
    results = cursor.fetchall()
    CodeID = int(results[0]["count(CodeID)"]) + 1
    print(CodeID)

# submit date
import time    
SubmitDate = time.strftime('%Y-%m-%d %H:%M:%S')

# language
Language = lang

# insert submission
with connection.cursor() as cursor:
    sql = "INSERT INTO code3 (CodeID, SubmitDate, Language) VALUES (%s, %s, %s)"
    r = cursor.execute(sql, (CodeID, SubmitDate, Language))
    connection.commit()

connection.close()


# return submit page
#####################################################################################
print("Content-Type: text/html\n")
print('''
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <meta name="author" content="kosakkun">
        <meta name="description" content="">
        <title>Endless Marathon</title>
    </head>
    <body>
        Success! : <a href="/submit.html">Submit</a>
    </body>
</html>
''')
