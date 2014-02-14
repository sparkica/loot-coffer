from flask import Flask
import tweepy
import urllib2
import json

app = Flask(__name__)


@app.route("/")
def hello():
	return ""


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
