folder2tumblr
=============

Uploads images from folder to tumblr.
Works with python2

### What it does
Provided a tumblog name, a folder path and a post state, this script uploads the image content of the folder to the specified tumblog.

It records every successful upload in a JSON file so that it won't reupload it again, and to keep track of what you have uploaded.

The first launch setups a prompt to create the necessary tokens, they are saved in a file for subsequent calls.

Also, the posts are dated with the image creation date.

### What it doesn't do (yet)
- Check upload limit.
- Give the ability to choose how many files to upload.
- Schedule uploads.

### Installation:
```sh
pip install -r requirements.txt 
```

### Usage:

```
folder2tumblr.py BLOGNAME FOLDER [POSTSTATE]
folder2tumblr.py -h | --help

Arguments:
    BLOGNAME  Blogname
    FOLDER=DIR  Folder
    POSTSTATE  the post state 'queue' or 'published' [default: published]
```
