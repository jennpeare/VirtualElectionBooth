from flask import Flask, render_template
from OpenSSL import SSL

context = SSL.Context(SSL.SSLv23_METHOD)
context.use_privatekey_file("./keys/key.pem")
context.use_certificate_file("./keys/cert.pem")

app = Flask(__name__)

@app.route("/")
def main():
    return render_template("test.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1234, debug=True, ssl_context=context)
