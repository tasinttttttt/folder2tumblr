folder2tumblr
=============

Uploads images from folder to tumblr, APIv2

The auth example is straight from https://gist.github.com/velocityzen/1242662


## What it does
Provided a tumblog name, a folder path, a json filename and a post state, this script uploads the content of the folder to the specified tumblog. It records every successful upload in a JSON file so that it won't reupload it again, and to keep track of what you have uploaded.

#### What it doesn't do (yet)
- [ ] Check upload limit
- [ ] Creating the JSON file if nothing is provided
- [ ] Give the ability to choose how many files to upload
- [ ] Schedule uploads

## Usage:

```
photo2tumblr.py BLOGNAME FOLDER JSONFILE [POSTSTATE]
photo2tumblr.py -h | --help

Arguments:
    BLOGNAME  Blogname
    FOLDER=DIR  Folder
    JSONFILE=FILE  json file name
    POSTSTATE  the post state 'queue' or 'published' [default: published]
```
