from flask import Flask, make_response, abort ,request, redirect, render_template
import datetime,time, os, re
from unidecode import unidecode
from subprocess import Popen, PIPE, STDOUT
from datetime import datetime

DEBUG = False
HOST = "localhost"
PORT = 8000
SOLVE = None #IP of SOLVE, none disables
WEB_INTERFACE = True
WHITE_LIST = "teams" #lookup file with teamnames and locations, None not to load
# IP 	TEAM_NAME	LOCATION tab separated
MIN_INTERVAL = 10 #s between requests to print
MAX_CHARS = 80*1000
MAX_PAGES = 16

LANG_A2PS = {
	'c': 'c',
	'cpp': 'c++',
	'java': 'java',
	'pas': 'pascal',
}

app = Flask(__name__)
last_print = {}

def get_team_details(ip):
	if WHITE_LIST is None:
		return (ip,ip,ip)
	with open(WHITE_LIST) as wl:
		while True:
			line = wl.readline()
			if not line:
				break
			fields = line.split('\t')
			if ip==fields[0]:
				return (
					fields[0].rstrip(),
					fields[0].rstrip() if len(fields)<=1 else fields[1].rstrip(),
					fields[0].rstrip() if len(fields)<=2 else fields[2].rstrip(),
				)
	return None

def send_to_printer( code, syntax="text", filename="printout", team_name="", team_ip="", check_team_names = True):
	if check_team_names:
		team_ip = re.sub('[^0-9.]+', '', team_ip)
		team_name = re.sub('[^0-9a-zA-Z._-]+', '', team_name)
	header = "team: {}, komputer: {}".format(team_name,team_ip)
	filename = " "+re.sub('[^0-9a-zA-Z.]+', '', filename)
	footer = "{}".format(datetime.fromtimestamp(time.time()).strftime("%d.%m.%Y %X"))
	header, footer = unidecode(header), unidecode(footer)
	a2ps_lang = LANG_A2PS.get(syntax, None)

	pretty_print = ""
	if a2ps_lang is not None:
		pretty_print = "-E{}".format(a2ps_lang)

	cmd = "a2ps %s -XISO-8859-2 --tabsize=4 --pages=1-%d --stdin=\"%s\" --header=\"%s\" --left-footer=\"%s\" "%( pretty_print, MAX_PAGES, filename , header, footer)
	p = Popen(cmd,shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE)
	output, errors = p.communicate(input=code.encode("iso-8859-2", "replace"))
	print(output)
	print(errors)


@app.route('/', methods=['GET'])
def root():
	if WEB_INTERFACE:
		return redirect('/form/')
	return make_response('<h1>PRINT SERVER</h1>')

if WEB_INTERFACE:

	@app.route('/form/', methods=['GET'])
	def show_form():
		return render_template("form.html")

	@app.route('/form/submit', methods=['POST'])
	def process_form():
		ip = request.remote_addr
		td = get_team_details(ip)
		if td is None:
			abort(403)

		print(td)
		code = str(request.form.get('code'))[:MAX_CHARS] or None
		syntax = str(request.form.get('lang'))[:32] or None
		filename = str(request.form.get('filename'))[:32] or None

		if not code:
			return make_response('<h1>Include code</h1>')

		if not filename:
			return make_response('<h1>Include filename</h1>')

		if ip in last_print:
			if (datetime.now()-last_print[ip]).total_seconds()<MIN_INTERVAL:
				return make_response('Too many print requests! Slow down!')

		last_print[ip] = datetime.now()

		team_name = td[1]
		team_loc = td[2]

		send_to_printer(code, syntax, filename, team_name, team_loc, False)

		return make_response('<h1>OK </h1><a href="/form/">go back</a>')

if SOLVE is not None:
	### show form
	@app.route('/print/', methods=['GET'])
	def show_form():
	    return make_response("""
	<form method="post">
		<p><h3>tresc</h3>
			<input type="text" name="content"></input>
			<!--<textarea rows="16" cols="80" name="text"></textarea>-->
		</p>
		<p><h3>lang</h3>
		<input type="text" name="filename" placeholder="filename"></input>
		<select name="lang">
			<option value="cpp">c++</option>
			<option value="c">c</option>
			<option value="pas">pascal</option>
			<option value="text">text</option>

		</select>
		</p>
		<p><h3>team</h3>
		<input type="text" name="ip" placeholder="ip teamu"></input>
		<input type="text" name="name" placeholder="nazwa teamu"></input>
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
		code = request.form.get('content') or None
		syntax = request.form.get('lang') or None
		filename = request.form.get('filename') or None
		team_ip = request.form.get('ip') or ""
		team_name = request.form.get('name') or ""
		if code is None or syntax is None:
			abort(400)
		send_to_printer(code,syntax,filename, team_name, team_ip)
		return make_response('ok')


### other
@app.errorhandler(404)
def not_found(error):
    return make_response('<h1> 404 </h1>')

if __name__ == '__main__':
    app.run(debug=DEBUG,host=HOST, port=PORT)
