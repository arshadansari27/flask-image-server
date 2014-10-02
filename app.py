import os
import urlparse
import requests
import redis
from PIL import Image
from StringIO import StringIO
from flask import Flask, request, send_file, redirect, render_template
from media import sanitze, ratio, measurements
import random


REDIS_URL = urlparse.urlparse(os.environ.get('REDISCLOUD_URL', 'redis://:@localhost:6379/'))

r = redis.StrictRedis(host=REDIS_URL.hostname, port=REDIS_URL.port, password=REDIS_URL.password)

app = Flask(__name__)

app.config['DEBUG'] = True
"""
if os.environ.get('DEVELOPMENT'):
	app.config['DEBUG'] = True
else:
	app.config['DEBUG'] = False
"""
ext2conttype2 = {
	"jpg": "JPEG",
	"jpeg": "JPEG",
	"png": "PNG",
	"gif": "GIF",
	"image/jpeg": "JPEG",
	"image/png": "PNG",
	"image/gif": "GIF"
}


ext2conttype = {"jpg": "image/jpeg",
	"jpeg": "image/jpeg",
	"png": "image/png",
	"gif": "image/gif"
}

@app.route('/media/upload', methods=['GET', 'POST'])
def uploader():
	if request.method=='POST':
		try:
			file = request.files['file']
			if file and file.filename:
				filename = file.filename
				extension = filename[filename.rfind(".")+1:].lower()
				content_type = ext2conttype[extension]
				image = Image.open(file)
				buff_img = StringIO()
				image.seek(0)
				image.save(buff_img, ext2conttype2[extension])
				key = "%s.%s.%s" % (random.random(), random.random(), random.random())
				print "KEY:", key
				r.set("Image-%s" % key, buff_img.getvalue())
				r.set("Content-type-%s" % key, content_type)
				buff_img.seek(0)	
				#return send_file(buff_img, mimetype='image/jpg')
				return key
		except:
			return 'Image Upload did not go well', 500
    	return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''


@app.route('/media/get/<img_id>', methods=['GET'])
def get_image(img_id):
	data = r.get('Image-%s' % img_id)
	content_type = r.get('Content-type-%s' % img_id)
	buff = StringIO()
	buff.write(data)
	buff.seek(0)
	print content_type
	return send_file(buff, mimetype=content_type)

@app.route('/media/get/thumbnail/<img_id>', methods=['GET'])
def get_image_thumbnail(img_id):
	height = request.args.get('height')
	width = request.args.get('width')

	data = r.get('Image-%s' % img_id)
	content_type = r.get('Content-type-%s' % img_id)
	buff = StringIO()
	buff.write(data)
	buff.seek(0)
	if height is None or width is None:
		return send_file(buff, mimetype=content_type)
	image = Image.open(buff)
	desired_width, desired_height = measurements(image, width, height)
	buffer_image = StringIO()
	print "Numbers is", desired_width, desired_height
	resized_image = image.resize((desired_width, desired_height), Image.ANTIALIAS)
	resized_image.save(buffer_image, ext2conttype2[content_type], quality=90)
	buffer_image.seek(0)
	return send_file(buffer_image, mimetype=content_type)


if __name__ == '__main__':
	app.run()
