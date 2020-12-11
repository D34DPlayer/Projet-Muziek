from . import parseVideoId


def test_parse_video_id():
	valid_links = [
		'https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLEiaJbmJ2m0G52-gMKEmmRq_4t2h9x4Nd&index=1',
		'https://www.youtube.com/watch?index=1&list=PLEiaJbmJ2m0G52-gMKEmmRq_4t2h9x4Nd&v=dQw4w9WgXcQ',
		'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
		'https://youtube.com/watch?v=dQw4w9WgXcQ',
		'http://www.youtube.com/watch?v=dQw4w9WgXcQ',
		'http://youtube.com/watch?v=dQw4w9WgXcQ',
		'dQw4w9WgXcQ'
	]
	invalid_links = [
		'https://www.youtube.com/feed/trending',
		'https://www.youtube.com/watch?list=PLEiaJbmJ2m0G52-gMKEmmRq_4t2h9x4Nd&index=1',
		'https://www.youtube.com/watch?v=dQw4w9Wg~~~',
		'https://www.youtube.com/watch?v=dQw4w9Wgééé',
		'https://www.youtube.com/watch?v=dQw4w9WgXcQi',
		'https://www.youtube.com/watch?v=dQw4w9Wg',
		'dQw4w9WgX@Q',
		'dQw4w9WgX',
		'dQw4w9WgXqsdl'
	]

	for link in valid_links:
		assert parseVideoId(link) == 'dQw4w9WgXcQ'

	for link in invalid_links:
		try:
			parseVideoId(link)
		except ValueError:
			pass
		else:
			assert False, link
