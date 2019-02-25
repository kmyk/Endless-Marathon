#!/usr/bin/env python3
import cgi
import subprocess
import pymysql.cursors

form = cgi.FieldStorage()

connection = pymysql.connect(
    host        = "localhost",
    user        = "root",
    password    = "",
    db          = "submit",
    charset     = "utf8",
    cursorclass = pymysql.cursors.DictCursor)

CodeID = form["codeid"].value

with connection.cursor() as cursor:   
    sql = "select * from code4 where CodeID=%s";
    cursor.execute(sql, (CodeID))
    results = cursor.fetchall()[0]
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
            <style>.CodeMirror {border: 1px solid #CCCCCC; height: 600px}</style>
            
            
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
                        <h4 class="underlined">Code</h4>
                        <br>
                        <textarea id="editor" class = "codearea" name="source_code">''' + results["CodeData"] + '''</textarea>
                        <script>
                            CodeMirror.fromTextArea(document.getElementById("editor"), {
                                mode: "text/x-csrc",
                                lineNumbers: true,
                            });
                        </script>
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
        
    </html>''')
                  
connection.close()
