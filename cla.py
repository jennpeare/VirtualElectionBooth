from flask import Flask, render_template, request
from OpenSSL import SSL
import string, random

#cla use private key

context = SSL.Context(SSL.SSLv23_METHOD)
context.use_privatekey_file("./keys/key.pem")
context.use_certificate_file("./keys/cert.pem")

cla = Flask(__name__)

eligible_voters = { "100" : ["Jenny", "Shi", False],
                    "200" : ["Vicki", "Shen", False],
                    "300" : ["Bob", "Builder", False] }

@cla.route("/")
def main():
    return render_template("register.html")

@cla.route("/validation", methods=["POST"])
def validation():
    if request.method == "POST":
        message = validate_voters(request.form["first_name"], 
                request.form["last_name"], request.form["pwd"])


def generate_validation_number():
    lst = [random.choice(string.ascii_letters + string.digits) for n in xrange(30)]
    rand = "".join(lst)
    return rand

def validate_voters(first_name, last_name, pwd):
    eligible = False
    repeat = False
    validation_num = None
    if not first_name or not last_name or not pwd:
        return "Bad! You didn't fill out the form!"
    elif eligible_voters.has_key(pwd):
        voter = eligible_voters[pwd]
        if voter[0] == first_name and voter[1] == last_name:
            if voter[2] == False:
                validation_num = generate_validation_number()
                voter.append(validation_num)
                voter[2] = True
                eligible = True
            else:
                repeat = True
    
    if eligible == True and validation_num is not None:
        return first_name + ", your validation number is: " + validation_num
    elif repeat == True:
        return "You have already registered."
    else:
        return "You're not eligible to vote."

if __name__ == "__main__":
    cla.run(host="0.0.0.0", port=1234, debug=True, ssl_context=context)
