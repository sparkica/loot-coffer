def get_plugin_info(plugin_slug):
	#http://wpapi.org/api/type/slug.format
	json_res = urllib.urlopen(WP_API_GATEWAY + plug_slug + '.json').read()
	res = simplejson.loads(json_res)
	stats = {'name' : res['name'],
			'slug' : plug_slug,
			'rating': res['rating'],
			'avg_downloads' : res['average_downloads'],
			'hits': res['hits']
			}
