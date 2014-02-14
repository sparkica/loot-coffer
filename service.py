import urllib
import simplejson

from flask import Flask, request, jsonify, json
from flask import render_template, redirect


app = Flask(__name__)


WP_API_GATEWAY = "http://wpapi.org/api/plugin/"

def get_wp_plugin_info(plugin_slug):
	print 'in helpers...'
	#http://wpapi.org/api/type/slug.format

	print 'Plugin slug #2', plugin_slug

	json_res = urllib.urlopen(WP_API_GATEWAY + plugin_slug + '.json').read()

	#print json_res
	res = simplejson.loads(json_res)
	print "got json"
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

	print 'here'

	if request.method == 'GET':
		print 'here too'
		slugs_arg = request.args.get('q')
		print "Slug arg: ", slugs_arg

		if slugs_arg:
			plug_slugs = slugs_arg.split(',')

			for plugin in plug_slugs:
				print "Plugin: ", plugin
				stats = get_wp_plugin_info( plugin.strip() )
				print "Stats: ", stats
				all_stats.append(stats)
	else:
		all_stats = None

	print 'about to render things...'
	return render_template('wordpress.html', stats=all_stats)



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
	app.run(debug=True)
