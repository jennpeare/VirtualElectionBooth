from flask import Flask, render_template, request
from OpenSSL import SSL
import string, random

# ctf use public key

context = SSL.Context(SSL.SSLv23_METHOD)
context.use_privatekey_file("./keys/key.pem")
context.use_certificate_file("./keys/cert.pem")

ctf = Flask(__name__)

@ctf.route("/")
def main():
    return "hai"

if __name__ == "__main__":
    ctf.run(host="0.0.0.0", port=4321, debug=True, ssl_context=context)
