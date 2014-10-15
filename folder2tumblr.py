"""
Folder to tumblr

Usage:
  folder2tumblr.py BLOGNAME FOLDER JSONFILE [POSTSTATE]
  folder2tumblr.py -h | --help

Arguments:
    BLOGNAME  Blogname
    FOLDER=DIR  Folder
    JSONFILE=FILE  json file name
    POSTSTATE  the post state 'queue' or 'published' [default: published]
    
Options:
  -h --help               Show this screen
"""

import glob
import json
import os
from os.path import basename
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import collections
import time
import urllib2
import urlparse
import oauth2
from docopt import docopt
 
class APIError(StandardError):
    def __init__(self, msg, response=None):
        StandardError.__init__(self, msg)
 
class TumblrAPIv2:
    def __init__(self, consumer_key, consumer_secret, oauth_token, oauth_token_secret):
        self.consumer = oauth2.Consumer(consumer_key, consumer_secret)
        self.token = oauth2.Token(oauth_token, oauth_token_secret)
        self.url = "http://api.tumblr.com"
 
    def parse_response(self, result):
        content = json.loads(result)
        if 400 <= int(content["meta"]["status"]) <= 600:
            raise APIError(content["meta"]["msg"], result)
        return content["response"]
 
    def createPhotoPost(self, id, post):
        url = self.url + "/v2/blog/%s/post" %id
 
        img_file = post['data']
        del(post['data'])
        req = oauth2.Request.from_consumer_and_token(self.consumer,
                                                 token=self.token,
                                                 http_method="POST",
                                                 http_url=url,
                                                 parameters=post)
        req.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), self.consumer, self.token)
        compiled_postdata = req.to_postdata()
        all_upload_params = urlparse.parse_qs(compiled_postdata, keep_blank_values=True)
 
        for key, val in all_upload_params.iteritems():
            all_upload_params[key] = val[0]
 
        all_upload_params['data'] = open(img_file, 'rb')
        datagen, headers = multipart_encode(all_upload_params)
        request = urllib2.Request(url, datagen, headers)
 
        try:
            respdata = urllib2.urlopen(request).read()
        except urllib2.HTTPError, ex:
            return 'Received error code: ', ex.code
 
        return self.parse_response(respdata)
        
register_openers()
 
CONSUMER_KEY = ''
CONSUMER_SECRET = ''
OAUTH_TOKEN = ''
OAUTH_TOKEN_SECRET = '' 

api = TumblrAPIv2(CONSUMER_KEY, CONSUMER_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

###################################################

def photo_tumblr(blogname, folder, jsonfile, post_state="published"):
    DIR = folder
    FILE_MASK = ('*.jpg','*.png','*.gif','*.jpeg')
    BLOG = blogname + ".tumblr.com"
    uploadedPhotosList = DIR + "\\" + jsonfile
    print uploadedPhotosList
    fields = ["creation_time", "filename"]
    data = []
    if os.path.exists(uploadedPhotosList):
            with open(uploadedPhotosList, 'r+') as f:
                data = json.load(f)

    currentDirectoryFileList = []
    for files in FILE_MASK:
        currentDirectoryFileList.extend( glob.glob( os.path.join(DIR, files) ))
    currentDirectoryFileList.sort(key=os.path.getctime)

    currentDirectoryPhotosList = {}
    currentDirectoryPhotosList = collections.OrderedDict()
    photostoUpload = {}
    photostoUpload = collections.OrderedDict()

    for imagefile in currentDirectoryFileList:
        currentDirectoryPhotosList.update( { basename(imagefile) : time.ctime(os.path.getctime(imagefile)) } )


    ###########################################
            
            
    for img in currentDirectoryPhotosList:
        if img in data:
            if currentDirectoryPhotosList[img] == data[img]:
                print img + ' has already been uploaded'
        else:
            date  = time.gmtime(os.path.getctime(DIR + "\\" + img))
            post = {
                'type' : 'photo',
                'state' : post_state,
                'date' : time.strftime ("%Y-%m-%d %H:%M:%S", date),
                'data' : DIR + "\\" + img,
                'caption' : basename(img)
            }

            try:
                response = api.createPhotoPost(BLOG,post)
                if 'id' in response:
                    print (str(basename(img)) + " is published, with the id: " + str(response['id']) )
                    photostoUpload.update( { img : currentDirectoryPhotosList[img] } )
                    data.update(photostoUpload)
                    with open(uploadedPhotosList, 'r+') as f:
                            json.dump(data, f, indent = 4, sort_keys=True)
                            f.close()
                    #os.remove(DIR + "\\" + img)
                else:
                    print response
                    break

            except APIError:
                print "Error"
                break
            
    print "Done! Check " + uploadedPhotosList + " for the complete list of uploaded material."

if __name__ == "__main__":
    arguments = docopt(__doc__)

    blog_name = arguments['BLOGNAME']
    folder = arguments['FOLDER']
    jsonfile = arguments['JSONFILE']
    post_state = arguments['POSTSTATE']
    photo_tumblr(blog_name, folder, jsonfile, post_state)
