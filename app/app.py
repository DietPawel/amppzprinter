from flask import Flask, make_response, abort ,request # Response
import datetime,time
import os
#from subprocess import Popen, PIPE, STDOUT
from unidecode import unidecode

DEBUG = False

app = Flask(__name__)

def send_to_printer(header, code, syntax="text"):
	header = "{} -- sala {}, komputer {}".format(header,"","")
	footer = "{}".format(datetime.datetime.fromtimestamp(time.time()).strftime("%d.%m.%Y %X"))
	header, footer = unidecode(header), unidecode(footer)

	LANG_A2PS = {
		'c': 'c',
		'cpp': 'c++',
		'pas': 'pascal',
	}
	with open('code','wb') as codefile:
		codefile.write(code.encode("iso-8859-2", "replace"))
	a2ps_lang = LANG_A2PS.get(syntax, None)
	pretty_print = ""
	if a2ps_lang is not None:
		pretty_print = "-E{}".format(a2ps_lang)
	res = os.system("a2ps %s -XISO-8859-2 --stdin=\"%s\" --header=\"%s\" --left-footer=\"%s\" code | lp "%
		( pretty_print, "hardcoded filename", header, footer)
	)
	"""cmd = ["/usr/bin/a2ps","", pretty_print, "-XISO-8859-2",
		"--stdin={}".format("test"),
		"--header={}".format(header),
		"--left-footer={}".format(footer)]
	print(cmd)
	p = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE)
	a,b = p.communicate(input=code.encode("iso-8859-2", "replace"))
	print(b)"""

@app.route('/', methods=['GET'])
def root():
    return make_response('<h1>AMPPZ PRINT SERVER</h1>')

### show form
@app.route('/print/', methods=['GET'])
def show_form():
    return make_response("""
<form method="post">
	<p><h3>tresc</h3>
		<input type="text" name="code"></input>
		<!--<textarea rows="16" cols="80" name="text"></textarea>-->
	</p>
	<p><h3>syntax</h3>
	<select name="syntax">
		<option value="cpp">cpp</option>
		<option value="c">c</option>
		<option value="pas">pas</option>
		<option value="text">text</option>

	</select>
	</p>
	<input type="submit"></input>
</form>
""")

### print form contents
@app.route('/print/', methods=['POST'])
def print_form():
	#print(request.form)
	code = request.form.get('code')
	syntax = request.form.get('syntax')
	if code is None or syntax is None:
		abort(400)
	print(code+syntax)
	send_to_printer(request.remote_addr,code,syntax)
	return make_response('query ok')


### other
@app.errorhandler(404)
def not_found(error):
    #return make_response(jsonify({'error': 'Not found'}), 404)
    return make_response('<h1> 404 </h1>')

if __name__ == '__main__':
    app.run(debug=DEBUG,host="localhost", port=8000)
