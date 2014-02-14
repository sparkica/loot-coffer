from flask import Flask
import tweepy
import urllib2
import json
import urllib
import simplejson

from flask import Flask, request, jsonify, json
from flask import render_template, redirectž

app = Flask(__name__)


WP_API_GATEWAY = "http://wpapi.org/api/plugin/"


@app.route("/wp/")
def wp_stats(names=None, methods=['GET', 'POST']):

	stats = {}
	if request.method == 'GET':
		plug_slug = request.args.get('plugin')

		if plug_slug:
			#http://wpapi.org/api/type/slug.format
			json_res = urllib.urlopen(WP_API_GATEWAY + plug_slug + '.json').read()
			res = simplejson.loads(json_res)
			stats = [{'name' : res['name'],
					'slug' : plug_slug,
					'rating': res['rating'],
					'avg_downloads' : res['average_downloads'],
					'hits': res['hits']
					}]
		else:
			print "No plugin slug"
	else:
		stats = None

	return render_template('wordpress.html', name=plug_slug, stats=stats)


@app.route("/")
def index():
	return render_template('index.html')


@app.route("/twitter")
def twitter():
	keywords = ["#Zemanta", "@Zemanta"]
	twitter_filter = " OR ".join([keyword for keyword in keywords])

	auth = tweepy.OAuthHandler("dzSXOVSUDQNflGshi1xXMA", "kacIBRAZVVPwnVXhvFWJsn9DXTn1BFZOZQocUSckw6c")
	# next lines seem not to be needed but were present in the tutorial
	# Redirect user to Twitter to authorize
	# redirect_user(auth.get_authorization_url())
	# Get access token
	#auth.get_access_token("verifier_value")
	# Construct the API instance
	api = tweepy.API(auth)

	# TODO: Filter results better
	twitter_feed = ""
	public_tweets = api.search(q=twitter_filter, count=30)
	for tweet in public_tweets:
		record = json.loads(urllib2.urlopen("https://api.twitter.com/1/statuses/oembed.json?id=" + tweet.id_str).read())
		twitter_feed += record['html'] + "<br>"

	return "<html><body>" + twitter_feed + "</body></html>"

if __name__ == "__main__":
	app.run()
