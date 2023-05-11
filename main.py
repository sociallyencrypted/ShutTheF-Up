# flask app to get POST requests at /vote and return the results
import config
import subprocess
from flask import Flask, redirect, url_for, request
app = Flask(__name__)

censor = False

@app.route('/startVote')
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
    global censor
    voteNum = list(request.form)[0]
    print("Received vote: ", int(voteNum))
    if int(voteNum) >= 0:
        censor = True
    else:
        censor = False 
    return "Vote received"
    
if __name__ == '__main__':
   app.run(host='0.0.0.0', port=8080)