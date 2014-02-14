from flask import Flask
app = Flask(__name__)


@app.route("/")
def hello():
	return ""


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
