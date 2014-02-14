from flask import Flask
import tweepy
import urllib2
import urllib
import localsettings as settings

from flask import Flask, request, jsonify, json
from flask import render_template, redirect

app = Flask(__name__)


WP_API_GATEWAY = "http://wpapi.org/api/plugin/"

def get_wp_plugin_info(plugin_slug):

	json_res = urllib.urlopen(WP_API_GATEWAY + plugin_slug + '.json').read()
	res = simplejson.loads(json_res)
	stats = {'name' : res['name'],
			'slug' : plugin_slug,
			'version': res['version'],
			'updated': res['updated'],
			'rating': res['rating'],
			'avg_downloads' : res['average_downloads'],
			'hits': res['hits'],
			'total_downloads': res['total_downloads']
			}
	return stats



@app.route('/wp/')
def wp_stats(methods=['GET']):

	all_stats = []
	if request.method == 'GET':
		slugs_arg = request.args.get('q')
		if slugs_arg:
			plug_slugs = slugs_arg.split(',')

			for plugin in plug_slugs:
				stats = get_wp_plugin_info( plugin.strip() )
				all_stats.append(stats)
	else:
		all_stats = None

	return render_template('wordpress.html', stats=all_stats)



@app.route("/")
def index():
	return render_template('index.html')


@app.route("/twitter")
def twitter():
	keywords = ["#Zemanta", "@Zemanta"]
	twitter_filter = " OR ".join([keyword for keyword in keywords])

	auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_TOKEN, settings.TWITTER_CONSUMER_SECRET)
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


@app.route("/google")
def google():

	url = ('https://ajax.googleapis.com/ajax/services/search/web'
		   '?v=1.0&q=Paris')

	request = urllib2.Request(
		url, None, {'Referer': "http://www.zemanta.com/"})
	response = urllib2.urlopen(request).read()

	# Process the JSON string.
	result = json.loads(response)

	results = result['responseData']['results']
	for result in results:
		print result

	return "<html><body>" + str(results["responseData"]) + "</body></html>"

if __name__ == "__main__":
	app.run(debug=True)
