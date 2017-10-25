from flask import Flask, make_response, abort ,request
import datetime,time, os, re
from unidecode import unidecode

DEBUG = False
HOST = "localhost"
PORT = 8000
SOLVE = '127.0.0.1'

app = Flask(__name__)

def send_to_printer(header, code, syntax="text", filename="AMPPZ 2017"):
	#header = "{} -- sala {}, komputer {}".format(header,"","")
	footer = "{}".format(datetime.datetime.fromtimestamp(time.time()).strftime("%d.%m.%Y %X"))
	header, footer = unidecode(header), unidecode(footer)
	with open('code','wb') as codefile:
		codefile.write(code.encode("iso-8859-2", "replace"))
	LANG_A2PS = {
		'c': 'c',
		'cpp': 'c++',
		'pas': 'pascal',
	}
	a2ps_lang = LANG_A2PS.get(syntax, None)
	pretty_print = ""
	if a2ps_lang is not None:
		pretty_print = "-E{}".format(a2ps_lang)
	res = os.system("cat code | a2ps %s -XISO-8859-2 --stdin=\"%s\" --header=\"%s\" --left-footer=\"%s\" | lp "%
		( pretty_print, filename, header, footer)
	)
	return res

@app.route('/', methods=['GET'])
def root():
    return make_response('<h1>AMPPZ PRINT SERVER</h1>')

### show form
@app.route('/print/', methods=['GET'])
def show_form():
    return make_response("""
<form method="post">
	<p><h3>tresc</h3>
		<input type="text" name="content"></input>
		<!--<textarea rows="16" cols="80" name="text"></textarea>-->
	</p>
	<p><h3>syntax</h3>
	<select name="lang">
		<option value="cpp">c++</option>
		<option value="c">c</option>
		<option value="pas">pascal</option>
		<option value="text">text</option>

	</select>
	</p>
	<input type="submit"></input>
</form>
""")

### print form contents
@app.route('/print/', methods=['POST'])
def print_form():
	if(not request.remote_addr == SOLVE):
		abort(400)
	print(request.form)
	code = request.form.get('content')
	syntax = request.form.get('lang')
	filename = request.form.get('filename')
	team_ip = request.form.get('ip')
	team_name = request.form.get('name')
	if code is None or syntax is None:
		abort(400)
	#print(code+syntax)
	res = send_to_printer(request.remote_addr,code,syntax)
	return make_response('query result: '+str(res))


### other
@app.errorhandler(404)
def not_found(error):
    return make_response('<h1> 404 </h1>')

if __name__ == '__main__':
    app.run(debug=DEBUG,host=HOST, port=PORT)
