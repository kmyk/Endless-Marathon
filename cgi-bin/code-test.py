#!/usr/bin/env python3
import cgi
import subprocess

form = cgi.FieldStorage()

source_code = ""
stdin_data  = ""
stdout_data = ""
stderr_data = ""

lang = form["lang-sel"].value

if "source_code" in form:
	source_code = form["source_code"].value
file = open("./cgi-bin/code-test/a.cpp", 'w')
file.write(source_code)
file.close()

if "stdin" in form:
	stdin_data = form["stdin"].value
file = open("./cgi-bin/code-test/input.txt", 'w')
file.write(stdin_data)
file.close()

cmd = "g++ ./cgi-bin/code-test/a.cpp -o ./cgi-bin/code-test/a.out -std=c++11 && time ./cgi-bin/code-test/a.out < ./cgi-bin/code-test/input.txt"
proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout_data = proc.stdout.decode("utf8")
stderr_data = proc.stderr.decode("utf8")

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
                    <h3>Code Test</h3>
                    <br>
                    <br>
                    <form name="form" method="POST" action="/cgi-bin/code-test.py">
                        <div class="row">
                            <div class="col of-8">
                                Source Code : <br>
                                <textarea id="editor" class = "codearea" name="source_code">''' + str(source_code) + '''</textarea>
                                <script>
                                    CodeMirror.fromTextArea(document.getElementById("editor"), {
                                        mode: "text/x-csrc",
                                        lineNumbers: true,
                                    });
                                </script>
                                <br>
                                <div class="input-container buttons"><button type="submit" name="submit" class="btn blue">Run</button></div>
                            </div>
                            <div class="col of-4">
                                Language : <br>
                                <div class="input-container select">
                                    <select name="lang-sel">
                                        <optgroup label="some set">
                                            <option value="cpp">C++</option>
                                            <option value="java">Java</option>
                                            <option value="python">Python</option>
                                        </optgroup>
                                    </select>
                                </div><br>
                                Standard Input : <br>
                                <textarea class = "codearea" name="stdin" rows="4">''' + str(stdin_data) + '''</textarea><br><br>
                                Standard Output : <br>
                                <textarea class = "codearea" readonly name="stdout" rows="4" style="background-color:#F8F8F8">''' + str(stdout_data) + '''</textarea><br><br>
                                Standard Error : <br>
                                <textarea class = "codearea" readonly name="stderr" rows="4" style="background-color:#F8F8F8">''' + str(stderr_data) + '''</textarea>
                            </div>
                        </div>
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
