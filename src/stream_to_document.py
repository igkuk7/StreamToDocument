#!/usr/bin/python

import sys, getopt, urlparse, urllib, urllib2, json, datetime, os
from PIL import Image,  ImageFont, ImageDraw

DATE_FORMAT = "%d/%m/%Y"

ARGS = {
	"-f": ( "Start Date", "Start Date to search from, format DD/MM/YYYY" ),
	"-t": ( "End Date",   "End Date to search to, format DD/MM/YYYY"     ),
	"-o": ( "Output Directory",   "All fetched images will have a caption added to them and placed in this directory"     ),
}

# TODO: global vars for URLs etc..
API_URL = "https://api.instagram.com"
API_AUTH_URL = API_URL+"/oauth/authorize/"
API_USERS_URL = API_URL+"/v1/users/"

# TODO: from config
REDIRECT_URL = "https://github.com/igkuk7/StreamToDocument"
CLIENT_ID = "418b90ba16fe4ab3a55727087d8d845b"
ACCESS_TOKEN = "1635247040.418b90b.d30cce44f28c47f5a6ddae5e49a77bad"

def get_user_posts(start_date=None, end_date=None):
	params = {}
	if start_date is not None:
		params["min_timestamp"] = start_date.strftime("%s")
	if end_date is not None:
		params["max_timestamp"] = end_date.strftime("%s")

	posts = api_call(API_USERS_URL+"self/media/recent/", params);
	return posts


def api_call(url, params={}):
	params["access_token"] = ACCESS_TOKEN
	result = urllib2.urlopen(url+"?"+urllib.urlencode(params))
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
	ACCESS_TOKEN = result_url.split("#")[-1]
	if ACCESS_TOKEN == "":
		print result_url_args
		error("Excepted access_token in result url")


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


def get_post_data(output_dir, post):
	created = datetime.datetime.fromtimestamp(float(post["created_time"]))
	image_url = post["images"]["standard_resolution"]["url"]
	extension = post["images"]["standard_resolution"]["url"].split(".")[-1]
	post_data = {
		"created"   : created,
		"caption"   : post["caption"]["text"],
		"image_url" : image_url,
		"extension" : extension,
		"file_name" : output_dir + "/" + created.strftime("%s") + "." + extension,
	}

	urllib.urlretrieve(post_data["image_url"], post_data["file_name"])

	post_data["captioned_file_name"] = add_caption_to_image(post_data["file_name"], post_data["caption"])

	return post_data



def add_caption_to_image(image_file_name, caption):
	extension = image_file_name.split(".")[-1]
	caption_image_file_name = image_file_name.replace("."+extension, "-captioned."+extension)

	# open the image and write the caption to it
	image = Image.open(image_file_name)
	draw = ImageDraw.Draw(image)
	#font = ImageFont.truetype("arial.ttf", 16)
	caption_size = draw.textsize(caption)
	border = 10
	draw.text((border, image.size[1]-border-caption_size[1]), caption, (255,255,255))
	image.save(caption_image_file_name)

	return caption_image_file_name


def main(script_name, argv):
	try:
		opts, args = getopt.getopt(argv, "h"+"".join(map(lambda x: x+":", ARGS.keys())))
	except getopt.GetoptError as e:
		print e
		usage(1)

	# unkown args are dealt with by getopt
	# so just grab are args and go here
	script_args = {}
	for opt, arg in opts:
		if opt == "-h":
			usage(0)
		elif opt in ARGS:
			script_args[opt] = arg

	# parse incoming date/times
	start_date = get_datetime( script_args["-f"] if "-f" in script_args else "" )
	end_date   = get_datetime( script_args["-t"] if "-t" in script_args else "" )

	# output dir
	if "-o" not in script_args:
		error("Missing Output Directory")
	output_dir = script_args["-o"]
	if not os.path.isdir(output_dir):
		os.makedirs(output_dir)

	# authenticate
	authenticate()
	posts = get_user_posts(start_date, end_date)

	#posts_json = '{"pagination":{},"meta":{"code":200},"data":[{"attribution":null,"tags":["manofsteel"],"type":"image","location":null,"comments":{"count":0,"data":[]},"filter":"Valencia","created_time":"1435771379","link":"https:\/\/instagram.com\/p\/4mg0Own-YF\/","likes":{"count":0,"data":[]},"images":{"low_resolution":{"url":"https:\/\/scontent.cdninstagram.com\/hphotos-xfa1\/t51.2885-15\/s320x320\/e15\/11350949_1611348742467118_545601823_n.jpg","width":320,"height":320},"thumbnail":{"url":"https:\/\/scontent.cdninstagram.com\/hphotos-xfa1\/t51.2885-15\/s150x150\/e15\/11350949_1611348742467118_545601823_n.jpg","width":150,"height":150},"standard_resolution":{"url":"https:\/\/scontent.cdninstagram.com\/hphotos-xfa1\/t51.2885-15\/e15\/11350949_1611348742467118_545601823_n.jpg","width":640,"height":640}},"users_in_photo":[],"caption":{"created_time":"1435771379","text":"Awful, boring, with a decent ending #manofsteel","from":{"username":"igkuk7","profile_picture":"https:\/\/instagramimages-a.akamaihd.net\/profiles\/anonymousUser.jpg","id":"1635247040","full_name":""},"id":"1019646695230662304"},"user_has_liked":false,"id":"1019646692395312645_1635247040","user":{"username":"igkuk7","profile_picture":"https:\/\/instagramimages-a.akamaihd.net\/profiles\/anonymousUser.jpg","id":"1635247040","full_name":""}}]}'
	#posts = json.loads(posts_json)

	for post in posts["data"]:
		post_data = get_post_data(output_dir, post)

		print post_data




def usage(exit_status, message=""):
	sys.stdout.write("stream_to_document.py")
	for arg in ARGS.keys():
		sys.stdout.write(arg+ " ["+ARGS[arg][0]+"]")
	print " "
	print message
	for arg in ARGS.keys():
		print ARGS[arg][0] + " - " + ARGS[arg][1]
	sys.exit(exit_status)


def error(message=""):
	print message
	sys.exit(1)


if __name__ == "__main__":
	# strip to first arg, script name
	main(sys.argv[0], sys.argv[1:])