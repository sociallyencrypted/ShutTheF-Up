# flask app to get POST requests at /vote and return the results
import config
import subprocess
import serial
from flask import Flask, redirect, url_for, request, render_template
app = Flask(__name__)

censor = False

yes_count = 0
no_count = 0

@app.route('/', methods=['GET', 'POST'])
def vote_page():
    global yes_count, no_count
    if request.method == 'POST':
        if 'yes' in request.form:
            yes_count += 1
        elif 'no' in request.form:
            no_count += 1
        elif 'start' in request.form:
            return render_template('vote.html', yes_count=yes_count, no_count=no_count)
        elif 'submit' in request.form:
            return redirect(url_for('vote'))
    return render_template('vote.html', yes_count=yes_count, no_count=no_count)

@app.route('/startVote', methods=['GET', "POST"])
def startVote():
    subprocess.Popen(["python3", "audioHandler.py"])
    return "Vote started"
    
    
@app.route('/status', methods = ['GET'])
def status():
    global censor
    if censor:
        return "Censoring"
    else:
        return "Not Censoring"

@app.route('/vote',methods = ['POST'])
def vote():
    global yes_count, no_count, censor
    vote_result = yes_count - no_count
    if vote_result >= 0:
        censor = True
    else:
        censor = False
    yes_count = 0  # Reset the counts for the next vote
    no_count = 0
    return f'{vote_result}'

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=8080)