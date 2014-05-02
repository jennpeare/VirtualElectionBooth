#from Crypto.Hash import SHA
#from Crypto.PublicKey import RSA
from flask import Flask, render_template, request
from OpenSSL import SSL
import string, random, requests

#cla use private key

# SSL setup
context = SSL.Context(SSL.SSLv23_METHOD)
context.use_privatekey_file("./keys/key.pem")
context.use_certificate_file("./keys/cert.pem")

cla = Flask(__name__)

# list of eligible voters
eligible_voters = { "100" : ["Jenny", "Shi", False],
                    "200" : ["Vicki", "Shen", False],
                    "300" : ["Steph", "Yang", False],
                    "400" : ["Grace", "Chi", False],
                    "500" : ["Janice", "Tsai", False],
                    "600" : ["Yamini", "Kathari", False],
                  }

# stores CSRF token
session = {}

@cla.route("/")
def main():
    return render_template("cla_register.html")

@cla.route("/validation", methods=["POST"])
def validation():
    if request.method == "POST":
        return render_template("cla_validation.html",
          message = validate_voters(request.form["first"],
                                    request.form["last"],
                                    request.form["secret"]))

def send_to_ctf(validation_num):
    #h = SHA.new(validation_num).digest() # encryption
    #f = open("./keys/rsa", "r")
    #key = RSA.importKey(f.read())
    #sig = key.sign(h, key)
    pair = {"validation_num" : validation_num }
    req = requests.post("https://0.0.0.0:4321/add_voter", pair, verify=False)

def generate_valid_num(length):
    lst = [random.choice(string.ascii_letters + string.digits)
      for n in xrange(length)]
    rand = "".join(lst)
    return rand

def generate_random_str():
    lst = [random.choice(string.ascii_letters + string.digits)
      for n in xrange(30)]
    rand = "".join(lst)
    return rand

def validate_voters(first, last, secret):
    eligible = False # whether or not voter is eligible to register
    repeat = False # whether voter has already registered
    validation_num = None
    if not first or not last or not secret:
        return "Please fill all of the fields."
    elif eligible_voters.has_key(secret):
        voter = eligible_voters[secret]
        if voter[0] == first and voter[1] == last:
            if voter[2] == False:
                validation_num = generate_valid_num(15)
                voter.append(validation_num) # add validation num to voter
                send_to_ctf(validation_num) # send validation number to CTF
                voter[2] = True # update: voter has alredy registered
                eligible = True
            else:
                repeat = True

    if eligible == True and validation_num is not None:
        return first + " " + last + ", your validation number is: " + validation_num
    elif repeat == True:
        return "You have already registered."
    else:
        return "You are not eligible to register."

# CSRF check before each request
@cla.before_request
def csrf_protect():
    if request.method == "POST":
        token = session["csrf_token"]
        if not token or token != request.form["csrf_token"]:
            return "CSRF"

def generate_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = generate_random_str()
    return session["csrf_token"]

cla.jinja_env.globals["csrf"] = generate_csrf_token() #global csrc token

if __name__ == "__main__":
    cla.run(host="0.0.0.0", port=1234, debug=True, ssl_context=context)
