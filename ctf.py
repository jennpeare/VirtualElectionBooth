from Crypto.Signature import PKCS1_PSS as PKCS
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from base64 import b64encode, b64decode
from flask import Flask, render_template, request
from OpenSSL import SSL
import string, random, requests

# SSL setup
context = SSL.Context(SSL.SSLv23_METHOD)
context.use_privatekey_file("./keys/key.pem")
context.use_certificate_file("./keys/cert.pem")

ctf = Flask(__name__)

voters = {} # rand_id : { "valid_num" : valid_num, "vote": vote }
validation_numbers = {} # valid_num : ifVoted
votes = { "dem" : 0, "rep" : 0, "tea" : 0 }
names = []

# stores CSRF token
session = {}

@ctf.route("/")
def main():
    return render_template("ctf_vote.html")

@ctf.route("/add_voter", methods=["POST"])
def add_voter():
    if request.method == "POST":
        signature = request.form["digsig"]
        valid_num = request.form["valid_num"]
        verified = False
        if verify_dig_sig(signature, valid_num):
            validation_numbers[valid_num] = False
    return "add_voter"

@ctf.route("/get_name", methods=["POST"])
def get_names():
    if request.method == "POST":
        signature = request.form["digsig"]
        name = request.form["name"]
        if verify_dig_sig(signature, name):
            names.append(name)
    return "get_name"

@ctf.route("/confirmation", methods=["POST"])
def confirmation():
    if request.method == "POST":
        message = validate_voter(request.form["rand_id"], request.form["valid_num"], request.form["party"])
        if "thanks" in message:
            request_voter_name(request.form["valid_num"])
        return render_template("ctf_confirmation.html", message = message)

@ctf.route("/results")
def display_results():
    return render_template("ctf_results.html", voters=voters, votes=votes, names=names)

def request_voter_name(valid_num):
    signature = create_dig_sig(valid_num)
    info = { "digsig" : signature , "valid_num" : valid_num }
    req = requests.post("https://0.0.0.0:1234/voter_name", data=info, verify=False)

def create_dig_sig(message):
    f = open("./keys/ctf_rsa", "r") # get ctf's private key
    key = RSA.importKey(f.read())
    h = SHA.new()
    h.update(message)
    signer = PKCS.new(key)
    signature = signer.sign(h)
    return b64encode(signature)

def verify_dig_sig(signature, message):
    f = open("./keys/rsa.pub", "r") # get cla's public key
    key = RSA.importKey(f.read())
    h = SHA.new()
    h.update(message)
    verifier = PKCS.new(key)
    if verifier.verify(h, b64decode(signature)):
        return True
    else:
        return False

def validate_voter(rand_id, valid_num, vote):
    eligible = False
    repeat = False
    if not rand_id or not valid_num or vote is None:
        return "Please fill all of the fields."
    elif voters.has_key(rand_id):
        return "Your random identification number is already taken, please try again."
    elif validation_numbers.has_key(valid_num):
        if validation_numbers[valid_num] == False:
            info = { "valid_num" : valid_num, "vote" : vote }
            voters[rand_id] = info # store voting info
            votes[vote] = votes[vote] + 1 # increase tally
            validation_numbers[valid_num] = True # update: voter already voted
            eligible = True
        else:
            repeat = True

    if eligible == True:
        party = ""
        if vote == "dem":
            party = "Democratic Party"
        elif vote == "rep":
            party = "Republican Party"
        elif vote == "tea":
            party = "Tea Party"
        return rand_id + ", thanks for voting for the " + party + "!"
    elif repeat == True:
        return "You have alredy voted."
    else:
        return "You are not registered to vote."

def generate_random_str():
    lst = [random.choice(string.ascii_letters + string.digits)
      for n in xrange(30)]
    rand = "".join(lst)
    return rand

# CSRF check before each request
@ctf.before_request
def csrf_protect():
    if request.method == "POST" and request.path != "/add_voter" and request.path != "/get_name":
        token = session["csrf_token"]
        if not token or token != request.form["csrf_token"]:
            return "CSRF"

def generate_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = generate_random_str()
    return session["csrf_token"]

ctf.jinja_env.globals["csrf"] = generate_csrf_token() #global csrc token

if __name__ == "__main__":
    ctf.run(host="0.0.0.0", port=4321, debug=True, threaded=True, ssl_context=context)
