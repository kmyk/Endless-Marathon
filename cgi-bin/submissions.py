#!/usr/bin/env python3
import cgi
import subprocess

form = cgi.FieldStorage()

######################################################################################
print("Content-Type: text/html\n")
print('''
<!DOCTYPE html>
<html>
    
    <!------------------------------------------------------------------------------------------------------>
    
    <head>
        
        <meta charset="utf-8">
        <meta name="author" content="kosakkun">
        <meta name="description" content="">
        <title>Endless Marathon</title>
        
        <!-- CSS -->
        <link href="/spark/css/spark.min.css" rel="stylesheet">
        <link href="/css/code.css" rel="stylesheet">
        
        <!-- JS -->
        <script src="https://code.jquery.com/jquery-3.3.1.min.js"></script>
        <script src="/spark/js/spark.min.js"></script>
        <script>
            $(function() {
                $("#header").load("/html/header.html");
                $("#footer").load("/html/footer.html");
            });
        </script>
        
        <!-- Create a simple CodeMirror instance -->
        <link rel="stylesheet" href="/codemirror/lib/codemirror.css">
        <script src="/codemirror/lib/codemirror.js"></script>
        <script src="/codemirror/mode/clike/clike.js"></script> 
        <style>.CodeMirror {border: 1px solid #CCCCCC; height: 430px}</style>
        
    </head>
    
    <!------------------------------------------------------------------------------------------------------>
    
    <body>
            
        <div class="container">
            
            <!-- header -->
            <div class="row">
                <div class="col of-2"></div>
                <div class="col of-8"><div id="header"></div></div>
                <div class="col of-2"></div>
            </div>
            
            <!-- main -->
            <div class="row">
                <div class="col of-2"></div>
                <div class="col of-8">
                    <h3>Submissions</h3>
                    <br>
                    <form name="form" method="GET" action="/cgi-bin/show-code.py">
                        <table class="tbl bordered center narrow">
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>Problem</th>
                                    <th>UserID</th>
                                    <th>time</th>
                                    <th>language</th>
                                    <th>Code</th>
                                </tr>
                            </head>
                            <tbody>''')
            
# show table
#####################################################################################
import pymysql.cursors

connection = pymysql.connect(
    host        = "localhost",
    user        = "root",
    password    = "",
    db          = "submit",
    charset     = "utf8",
    cursorclass = pymysql.cursors.DictCursor)

with connection.cursor() as cursor:   
    sql = "select * from code4";
    cursor.execute(sql)
    results = cursor.fetchall()
    for r in results:
        print("<tr>")
        print("<td>" + str(r["CodeID"]) + "</td>")
        print("<td>" + str(r["Problem"]) + "</td>")
        print("<td>" + str(r["UserID"]) + "</td>")
        print("<td>" + str(r["SubmitDate"]) + "</td>")
        print("<td>" + str(r["Language"]) + "</td>")
        print("<td><button type='submit' name='codeid' value=" + str(r["CodeID"]) + ">code</button></td>")
        print("</tr>")
              
connection.close()

#####################################################################################
print('''                   </tbody>
                        </table>
                    </form>
                </div>
                <div class="col of-2"></div>
            </div>
            
            <!-- footer -->
            <div class="row">
                <div class="col of-2"></div>
                <div class="col of-8"><div id="footer"></div></div>
                <div class="col of-2"></div>
            </div>
        
        </div>
        
    </body>
    
</html>
''')
