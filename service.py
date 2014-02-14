from flask import Flask
import tweepy
import urllib2
import urllib
import localsettings as settings
import feedparser
import sqlite3

from datetime import date

from flask import Flask, request, g, jsonify, json
from flask import render_template, redirect


app = Flask(__name__)


WP_API_GATEWAY = "http://wpapi.org/api/plugin/"
WP_SUPPORT_RSS_FEED = "http://wordpress.org/support/rss/plugin/"


def connect_db():
	"""Connects to the specific database."""
	rv = sqlite3.connect(settings.DATABASE)
	rv.row_factory = sqlite3.Row
	return rv	


def get_db():
	"""Opens a new database connection if there is none yet for the
	current application context.
	"""
	if not hasattr(g, 'sqlite_db'):
		g.sqlite_db = connect_db()
	return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
	"""Closes the database again at the end of the request."""
	if hasattr(g, 'sqlite_db'):
		g.sqlite_db.close()


@app.route('/downloads/')
def get_downloads_stats():
	db = get_db()
	cur_date = date.today()
	query = 'select Name, sum(Downloads) as TotalDownloads from Downloads where Date < "%s" group by Name;' % (cur_date.strftime('%Y-%m-%d'))
	print 'Query', query
	cur = db.execute(query)
	entries = cur.fetchall()
	return render_template('downloads.html', entries=entries)



def get_wp_support_feed_entries(plugin_slug, no_entries=-1):
	feed = feedparser.parse(WP_SUPPORT_RSS_FEED + plugin_slug)

	if no_entries < 0:
		return feed['entries']
	return feed['entries'][:no_entries]


@app.route('/wp/support/')
def wp_supportfeeds(methods=['GET']):
	all_entries = []
	if request.method == 'GET':
		slugs_arg = request.args.get('q')
		no_entries = int(request.args.get('entries')) if request.args.get('entries') is not None else -1
		details_arg = request.args.get('details')
		details = details_arg.split(',') if details_arg is not None else []

		if slugs_arg:
			plug_slugs = slugs_arg.split(',')

			for plugin in plug_slugs:
				entries = get_wp_support_feed_entries( plugin.strip(), no_entries )
				all_entries.append({'name': plugin, 'entries': entries})
	else:
		all_entries = None

	return render_template('wordpress_support.html', plugins=all_entries, details=details)


def get_wp_plugin_info(plugin_slug):

	json_res = urllib.urlopen(WP_API_GATEWAY + plugin_slug + '.json').read()
	res = json.loads(json_res)
	stats = {'name' : res['name'],
			'slug' : plugin_slug,
			'homepage_url': res['homepage'],
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


@app.route("/twitter/")
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


@app.route("/google/")
def google(methods=['GET']):

	blacklist = []
	try:
		with open("blacklist") as f:
			blacklist = f.readlines()
	except:
		pass

	query = None
	if request.method == 'GET':
		if 'q' in request.args:
			query = request.args.get('q')

	if query is None:
		query = "Zemanta"

	# 1w - one week
	last_week = "dateRestrict=7d"
	sort_option = "scoring=d"  # "sort=date-date:d"
	total_results = 30
	html_results = []
	start_index = 0

	rendered_html = []
	while start_index < total_results:
		url = "https://www.googleapis.com/customsearch/v1?key=%s&cx=%s&q=%s&num=10&start=%s&dateRestrict=w1&sort=date:d" %\
			(urllib2.quote(settings.GOOGLE_API_KEY), urllib2.quote(settings.GOOGLE_SEARCH_ENGINE_KEY), query, str(start_index+1))
		new_request = urllib2.Request(
			url, None, {'Referer': "http://www.zemanta.com/"})
		response = urllib2.urlopen(new_request).read()

		records = json.loads(response)
		for item in records['items']:
			if [urlx for urlx in blacklist if item['link'].startswith(urlx.strip())] != []:
				continue

			rendered_html = "<div>"
			rendered_html += item['title'] + "<br>"
			rendered_html += "<a href=" + item['link'] + ">%s</a>" % item['link'] + "<br>"
			rendered_html += item['snippet'] + "<br>"
			rendered_html += "</div>"
			html_results.append(rendered_html)
		count_items = len(records['items'])
		if count_items == 0:
			start_index = total_results
		else:
			start_index += count_items

	return """<html><head><script src="https://www.google.com/jsapi" type="text/javascript"></script></head><body>""" + "<br>".join(html_results) + "</body></html>"

if __name__ == "__main__":
	app.run(debug=True)
