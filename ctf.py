from flask import Flask, render_template, request
from OpenSSL import SSL
import string, random

# ctf use public key

# SSL setup
context = SSL.Context(SSL.SSLv23_METHOD)
context.use_privatekey_file("./keys/key.pem")
context.use_certificate_file("./keys/cert.pem")

ctf = Flask(__name__)

voters = {}
validation_numbers = {} # list of eligible voters | if they've already voted
votes = { "dem" : 0, "rep" : 0, "tea" : 0 }

# stores CSRF token
# session = {}

@ctf.route("/")
def main():
    return render_template("ctf_vote.html")

@ctf.route("/add_voter", methods=["POST"])
def add_voter():
    if request.method == "POST":
        validation_numbers[request.form["validation_num"]] = False
        return "YO"

@ctf.route("/confirmation", methods=["POST"])
def confirmation():
    if request.method == "POST":
        print "POST TO '/conf'"
        return render_template("ctf_confirmation.html",
          message = validate_voter(request.form["rand_id"],
                                    request.form["valid_num"],
                                    request.form["party"]))

@ctf.route("/voter_list")
def voter_list():
    return str(validation_numbers) + " " + str(votes)

def validate_voter(rand_id, valid_num, vote):
    eligible = False
    repeat = False

    if not rand_id or not valid_num or not vote:
        return "Please fill all of the fields."
    elif voters.has_key(rand_id):
        return "Your random identification number is already taken, please try again."
    elif validation_numbers.has_key(valid_num):
        if validation_numbers[valid_num] == False:
            voters[rand_id] = [valid_num, vote] # store voting info
            votes[vote] = votes[vote] + 1 # increase tally
            validation_numbers[valid_num] = True # update: voter already voted
            eligible = True
        else:
            repeat = True

    if eligible == True:
        return rand_id + ", thanks for voting for " + vote
    elif repeat == True:
        return "You have alredy voted."
    else:
        return "You are not registered to vote."

def generate_random_str():
    lst = [random.choice(string.ascii_letters + string.digits)
      for n in xrange(30)]
    rand = "".join(lst)
    return rand

# # CSRF check before each request
# @ctf.before_request
# def csrf_protect():
#     if request.method == "POST":
#         token = session["csrf_token"]
#         if not token or token != request.form["csrf_token"]:
#             return "CSRF"
#
# def generate_csrf_token():
#     if "csrf_token" not in session:
#         session["csrf_token"] = generate_random_str()
#     return session["csrf_token"]
#
# ctf.jinja_env.globals["csrf"] = generate_csrf_token() #global csrc token

if __name__ == "__main__":
    ctf.run(host="0.0.0.0", port=4321, debug=True, ssl_context=context)
