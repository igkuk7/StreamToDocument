#!/usr/bin/python

import sys, getopt, urlparse, urllib, urllib2, json, datetime, os, pprint
from PIL import Image,  ImageFont, ImageDraw

DATE_FORMAT = "%d/%m/%Y"

ARGS = {
	"-f": ( "Start Date", "Start Date to search from, format DD/MM/YYYY" ),
	"-t": ( "End Date",   "End Date to search to, format DD/MM/YYYY"     ),
	"-o": ( "File",   "HTML file to write to"     ),
}

DEBUG = False

# TODO: global vars for URLs etc..
API_URL = "https://api.instagram.com"
API_AUTH_URL = API_URL+"/oauth/authorize/"
API_USERS_URL = API_URL+"/v1/users/"

# TODO: from config
REDIRECT_URL = "https://github.com/igkuk7/StreamToDocument"
CLIENT_ID = "418b90ba16fe4ab3a55727087d8d845b"
ACCESS_TOKEN = ""

def get_user_posts(start_date=None, end_date=None):
	params = {}
	if start_date is not None:
		params["min_timestamp"] = start_date.strftime("%s")
	if end_date is not None:
		params["max_timestamp"] = end_date.strftime("%s")

	posts = api_call(API_USERS_URL+"self/media/recent/", params);
	post_data = posts["data"]
	while "pagination" in posts and "next_url" in posts["pagination"]:
		log("Fetching next page of results")
		posts = api_call(posts["pagination"]["next_url"], no_params=True);
		post_data += posts["data"]

	return post_data


def api_call(url, params={}, no_params=False):
	params["access_token"] = ACCESS_TOKEN
	full_url = url
	if not no_params:
		full_url += "?"+urllib.urlencode(params)
	log("API Call: "+full_url)
	result = urllib2.urlopen(full_url)
	data = json.loads(result.read())
	parse_api_errors(data)
	return data


def authenticate():
	global ACCESS_TOKEN
	if ACCESS_TOKEN != "":
		return

	print "Please visit the following URL to login. Once complete you will find yourself on our GitHub page. Copy the URL and paste it below then hit enter to continue"
	print API_AUTH_URL+"?client_id="+CLIENT_ID+"&redirect_uri="+urllib.quote(REDIRECT_URL)+"&response_type=token"
	result_url = raw_input("Result URL: ")
	result_url_parsed = urlparse.urlparse(result_url)
	result_url_args = urlparse.parse_qs(result_url_parsed[4])

	# check for error
	parse_api_errors(result_url_args)

	# get the access token, will be after the # at the end of the url
	ACCESS_TOKEN = result_url.split("#")[-1].split('=')[-1]
	if ACCESS_TOKEN == "":
		print result_url_args
		error("Excepted access_token in result url")
	log("Access Token: "+ACCESS_TOKEN)


def parse_api_errors(args):
	if "error" in args:
		error_message = "Error received!\n" + ",".join(result_url_args["error"])
		if "error_reason" in result_url_args:
			error_message += "\n" + ",".join(result_url_args["error_reason"])
		if "error_description" in result_url_args:
			error_message += "\n" + ",".join(result_url_args["error_description"])
		error(error_message)


def get_datetime(date=""):
	if date == "":
		return None

	parts = date.split("/")
	dt = datetime.datetime(int(parts[2]), int(parts[1]), int(parts[0]))
	return dt


def get_post_data(post):
	created = datetime.datetime.fromtimestamp(float(post["created_time"]))
	image_url = post["images"]["standard_resolution"]["url"]
	extension = post["images"]["standard_resolution"]["url"].split(".")[-1]
	post_data = {
		"created"   : created,
		"caption"   : post["caption"]["text"] if "caption" in post and post["caption"] is not None else "",
		"image_url" : image_url,
	}

	return post_data

def build_post_div(post_data):
	date = post_data["created"].strftime("%d/%m/%Y")
	log("Generating output for post on "+date+": "+post_data["caption"][0:20])
	img = "<img src='"+post_data["image_url"]+"' />"
	date = "<p><strong>"+date+"</strong></p>"
	caption = "<p>"+post_data["caption"]+"</p>"


	return "<div>\n\t"+img+"\n\t"+date+"\n\t"+caption+"\n</div>"



def main(script_name, argv):
	try:
		opts, args = getopt.getopt(argv, "hd"+"".join(map(lambda x: x+":", ARGS.keys())))
	except getopt.GetoptError as e:
		print e
		usage(1)

	# unkown args are dealt with by getopt
	# so just grab are args and go here
	script_args = {}
	for opt, arg in opts:
		if opt == "-h":
			usage(0)
		elif opt == "-d":
			DEBUG = True
		elif opt in ARGS:
			script_args[opt] = arg

	# parse incoming date/times
	start_date = get_datetime( script_args["-f"] if "-f" in script_args else "" )
	end_date   = get_datetime( script_args["-t"] if "-t" in script_args else "" )

	if "-o" not in script_args:
		usage(1, "Missing output file")
	output_file = script_args["-o"]

	# authenticate
	log("Authenticating")
	authenticate()

	# fetch posts
	log("Fetching user posts")
	posts = get_user_posts(start_date, end_date)

	# sort data earliest to latest
	divs = []
	for post in sorted(posts, reverse=False):
		post_data = get_post_data(post)
		html_div = build_post_div(post_data)
		divs.append(html_div)

	# generate file to write to
	log("Writing HTML file")
	f = open(output_file, "w")
	f.write("<html><body>\n")
	for div in divs:
		f.write(div+"\n")
	f.write("</body></html>")

	print "Generated HTML file: "+output_file


def usage(exit_status, message=""):
	print "StreamToDocument"
	print "v1.0"
	print "Generates a HTML document containing Instagram pictures and captions from the request date range"
	print ""
	print message
	print ""
	sys.stdout.write("Usage: stream_to_document.py")
	for arg in ARGS.keys():
		sys.stdout.write(" "+arg+ " ["+ARGS[arg][0]+"]")
	print "\n"
	for arg in ARGS.keys():
		print ARGS[arg][0] + " - " + ARGS[arg][1]
	sys.exit(exit_status)


def error(message=""):
	print message
	sys.exit(1)

def log(message):
	if DEBUG:
		print message


if __name__ == "__main__":
	# strip to first arg, script name
	main(sys.argv[0], sys.argv[1:])