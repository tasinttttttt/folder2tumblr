"""
Folder to tumblr

Usage:
  folder2tumblr.py BLOGNAME FOLDER [POSTSTATE]
  folder2tumblr.py -h | --help

Arguments:
    BLOGNAME  Blogname
    FOLDER=DIR  Folder
    POSTSTATE  the post state 'queue' or 'published' [default: published]

Options:
  -h --help               Show this screen
"""

import collections
from docopt import docopt
import glob
import json
import os
from os.path import basename
import pytumblr
from requests_oauthlib import OAuth1Session
import time
import yaml

YAML_FILE = os.path.join(os.getcwd(), '.tumblr_credentials')
JSON_FILE = os.path.join(os.getcwd(), 'uploaded_files.json')
FILE_TYPES = ('*.jpg','*.png','*.gif','*.jpeg')

class PrintColor:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

class ApiError(StandardError):
    def __init__(self, msg, response=None):
        StandardError.__init__(self, msg)

class TumblrApi:
    def __init__(self, consumer_key, consumer_secret, oauth_token, oauth_token_secret):
        self.client = pytumblr.TumblrRestClient(
            tokens['consumer_key'],
            tokens['consumer_secret'],
            tokens['oauth_token'],
            tokens['oauth_token_secret']
        )

    def parse_response(self, result):
        if ('meta' in result and 'msg' in result['meta']):
            if 400 <= int(result["meta"]["status"]) <= 600:
                raise ApiError(result["meta"]["msg"], result)
        return result

    def create_photo_post(self, blogname, file, state):
        #Creates a photo post using a local filepath
        date = time.gmtime(os.path.getctime(file))
        try :
            return self.parse_response(
                self.client.create_photo(
                    blogname,
                    date=time.strftime("%Y-%m-%d %H:%M:%S", date),
                    state=state,
                    data=file,
                    caption=basename(file)
                )
            )
        except ApiError as error:
            raise error

def new_oauth(yaml_path):
    '''
    Return the consumer and oauth tokens with three-legged OAuth process and
    save in a yaml file in the user's home directory.
    '''

    print('Retrieve consumer key and consumer secret from http://www.tumblr.com/oauth/apps')
    consumer_key = raw_input('Paste the consumer key here: ').strip()
    consumer_secret = raw_input('Paste the consumer secret here: ').strip()

    request_token_url = 'https://www.tumblr.com/oauth/request_token'
    authorize_url = 'https://www.tumblr.com/oauth/authorize'
    access_token_url = 'https://www.tumblr.com/oauth/access_token'

    # STEP 1: Obtain request token
    oauth_session = OAuth1Session(consumer_key, client_secret=consumer_secret)
    fetch_response = oauth_session.fetch_request_token(request_token_url)
    resource_owner_key = fetch_response.get('oauth_token')
    resource_owner_secret = fetch_response.get('oauth_token_secret')

    # STEP 2: Authorize URL + Rresponse
    full_authorize_url = oauth_session.authorization_url(authorize_url)

    # Redirect to authentication page
    print('\nPlease go here and authorize:\n{}'.format(full_authorize_url))
    redirect_response = raw_input('Allow then paste the full redirect URL here:\n').strip()

    # Retrieve oauth verifier
    oauth_response = oauth_session.parse_authorization_response(redirect_response)

    verifier = oauth_response.get('oauth_verifier')

    # STEP 3: Request final access token
    oauth_session = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        verifier=verifier
    )
    oauth_tokens = oauth_session.fetch_access_token(access_token_url)

    tokens = {
        'consumer_key': consumer_key,
        'consumer_secret': consumer_secret,
        'oauth_token': oauth_tokens.get('oauth_token').strip(),
        'oauth_token_secret': oauth_tokens.get('oauth_token_secret').strip()
    }

    yaml_file = open(yaml_path, 'w+')
    yaml.safe_dump(tokens, yaml_file, indent=2)
    yaml_file.close()

    return tokens

def folder2tumblr(client, blogname, folder, status):
    DIR = folder
    BLOG = blogname
    fields = ["creation_time", "filename"]
    data = {}
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r+') as f:
            data = json.load(f)
    else:
        f = open(JSON_FILE, 'w+')
        json.dump(data, f)
        f.close()

    currentDirectoryFileList = []
    for files in FILE_TYPES:
        currentDirectoryFileList.extend( glob.glob( os.path.join(DIR, files)))
    currentDirectoryFileList.sort(key=os.path.getctime)

    currentDirectoryPhotosList = {}
    currentDirectoryPhotosList = collections.OrderedDict()
    photostoUpload = {}
    photostoUpload = collections.OrderedDict()

    for imagefile in currentDirectoryFileList:
        currentDirectoryPhotosList.update( { basename(imagefile) : time.ctime(os.path.getctime(imagefile)) } )

    for img in currentDirectoryPhotosList:
        if img in data:
            if currentDirectoryPhotosList[img] == data[img]:
                print img + ' has already been uploaded'
        else:
            print data
            try:
                result = api.create_photo_post(blogname, os.path.join(folder, img), status)
                if 'id' in result:
                    print(PrintColor.BOLD + str(basename(img)) + PrintColor.END + ' ' + str(result['display_text']).lower() + ' as ' + PrintColor.BOLD + str(result['state']) + PrintColor.END + ' with id ' + PrintColor.BOLD + '#' + str(result['id']) + PrintColor.END)
                    photostoUpload.update( { img : currentDirectoryPhotosList[img] } )
                    data.update(photostoUpload)
                    with open(JSON_FILE, 'r+') as f:
                        json.dump(data, f, indent = 4, sort_keys=True)
                        f.close()
                else:
                    print result
                    break
            except ApiError as error:
                raise error

    print "Done! Check " + PrintColor.BOLD + JSON_FILE + PrintColor.END + " for the complete list of uploaded material."

if __name__ == '__main__':
    arguments = docopt(__doc__)

    if not os.path.exists(YAML_FILE):
        tokens = new_oauth(YAML_FILE)
    else:
        fd = open(YAML_FILE, "r")
        tokens = yaml.safe_load(fd)
        fd.close()

    if tokens:
        api = TumblrApi(tokens['consumer_key'], tokens['consumer_secret'], tokens['oauth_token'], tokens['oauth_token_secret'])
        try:
            folder2tumblr(api, arguments['BLOGNAME'], arguments['FOLDER'], 'published')
        except ApiError as error:
            print(error)
