#Virtual Election Booth: Report
Group Member: Jingfei Shi

##Final Design Protocol
All communications are carried out under SSL. Digital signatures are signed with the CLA/CTF's private keys, and verified with their public keys, respectively.

Registration:

	Voter -> CLA: { first name || last name || secret }
	CLA -> Voter: { acknowledgment || validation number }
	CLA -> CTF: { validation number || digital signature }
	
Voting:

	Voter -> CTF: { random identification number || validation number || vote }
	CTF -> Voter: { acknowledgment }
	CTF -> CLA: { validation number || digital signature }
	CLA -> CTF: { full name || digital signature }
	
Election Result:

	CTF -> Public:
		{ Number of votes for each party ||
		  For each party: list of supporters' random identification numbers ||
		  List of full names of people who voted }
	
##Implementation
The final implementation is a web application written in Python and served with Flask, a lightweight Python web framework. The CLA and CTF each has a flask instance, which translates to a server at a specified hostname and port number. 
	
	ctf.run(host="0.0.0.0", port=4321, debug=True, threaded=True, ssl_context=context)
	
Flask can map functions to URLs, which can be used as endpoints for communication. The functions can also render templates and output information to a HTML page. For example, the voter can fill out a form that sends a POST request to the `/validation` endpoint in the CTF. The CTF then takes the information, determines the proper response, and displays that as an HTML page at this endpoint.

The HTML pages are styled using the Foundation front-end framework, which includes preset CSS and javascript files. This is very useful to set up aesthetically appealing forms and buttons for the voters. All of the HTML files are stored in the `templates` folder, and the style files are in the `static` folder.

The `menu.py` is just an additional server that functions as the user interface. It contains links to the CLA, CTF, and the result page. There are two booleans in the file that enables/disables the links. They are used to indicate whether or not registration and voting is over.

###Secure Connection
The CLA and CTF both have a pair of public and private keys. They are generated using the `genrsa` command in the OpenSSL library. Similarly, the self signed certificates are also created to use for SSL connection.

In the python OpenSSL library, a context object must be defined. In this implementation, it is defined as using the `SSLv23_METHOD` and is associated with the certificates.

```
#SSL setup
context = SSL.Context(SSL.SSLv23_METHOD)
context.use_privatekey_file("./keys/key.pem")
context.use_certificate_file("./keys/cert.pem")
```
The context is included in the run method of the Flask server to ensure SSL connection.

###CSRF Protection
The forms on the web application are designed to prevent CSRF attacks. A hidden field in the form contains the CSRF token, which is a random string of characters generated by the CLA/CTF. 

	<input name="csrf_token" type="hidden" value="{{ csrf }}">

On the server side, the token is stored as a global token that is only valid for the current session.

	ctf.jinja_env.globals["csrf"] = generate_csrf_token() #global csrc token
