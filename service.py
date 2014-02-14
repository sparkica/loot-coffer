import urllib
import simplejson

from flask import Flask, request, jsonify, json
from flask import render_template, redirect
app = Flask(__name__)

import helpers

WP_API_GATEWAY = "http://wpapi.org/api/plugin/"


@app.route("/wp/")
def wp_stats(names=None, methods=['GET']):

	all_stats = []

	print 'here'

	if request.method == 'GET':
		slugs_arg = request.args.get('q')
		print "Slug arg: ", slugs_arg

		plug_slugs = slugs_arg.split(',')


		for plugin in plug_slugs:
			stats = get_plugin_info(plug_slug)
			all_stats.append(stats)
	else:
		all_stats = None

	return render_template('wordpress.html', name=plug_slug, stats=all_stats)


@app.route("/")
def index():
	return render_template('index.html')


@app.route("/twitter")
def twitter():
	keywords = ["zemanta"]
	twitter_filter = "+OR+".join(["%23s" + keyword for keyword in keywords])
	name = "Zemanta twiti"
	twitter_feed = """
	<div>
	<a class="twitter-timeline" href="https://twitter.com/search?q=%s" data-widget-id="434246345767936000">%s</a>
	<script>!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0],p=/^http:/.test(d.location)?'http':'https';if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src=p+"://platform.twitter.com/widgets.js";fjs.parentNode.insertBefore(js,fjs);}}(document,"script","twitter-wjs");</script>
	</div>
	""" % (twitter_filter, name)
	return "<html><body>" + twitter_feed + "</body></html>"


if __name__ == "__main__":
	app.run()
