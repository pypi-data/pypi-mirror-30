#!/usr/bin/env python

import os
import sys
import yaml
import shutil
from PIL import Image
from jinja2 import Environment, FileSystemLoader

default = {
    "base": "<!doctype html><html lang='en'><head><meta charset='utf-8'><link rel='stylesheet' href='/style.css'/><title></title></head><body>{% block content %}{% endblock %}</body></html>",
    "index": '{% extends "base.html" %}{% block content %}<h1><a href="{{config.url}}">{{config.name}}</a></h1><ul>{% for item in menu.items %}<li><a href="{{item.url}}">{{item.name}}</a></li>{% endfor %}</ul><div class="container"><h2><a href="/index.html">Index</a></h2> {% for picture in pictures%}<a href="{{picture.link}}"><img src="{{picture.linkSmall}}"/></a>{% endfor %}</div>{% endblock %}',
    "single": '{% extends "base.html" %} {% block content %} <h1><a href="{{config.url}}">{{config.name}}</a></h1> <ul> {% for item in menu.items %} <li><a href="{{item.url}}">{{item.name}}</a></li> {% endfor %} </ul> <div class="container"> <h2><a href="/{{picture.parent.name}}/index.html">{{picture.parent.name}}</a></h2> <img src="{{picture.linkLarge}}"/> </div> {% endblock %}',
    "list": ' {% extends "base.html" %} {% block content %} <h1><a href="{{config.url}}">{{config.name}}</a></h1> <ul> {% for item in menu.items %} <li><a href="{{item.url}}">{{item.name}}</a></li> {% endfor %} </ul> <div class="container"> <h2><a href="/{{album.name}}/index.html">{{album.name}}</a></h2> {% for picture in album.pictures%} <a href="{{picture.link}}"><img src="{{picture.linkSmall}}"/></a> {% endfor %} </div> {% endblock %}',
}


workingdir = os.getcwd()
PATH = workingdir
#PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_ENVIRONMENT = Environment(
    autoescape=False,
    loader=FileSystemLoader(os.path.join(PATH, 'assets')),
    trim_blocks=False)
 
 
def render_template(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)


class MenuItem:
    def __init__(self, name, url):
        self.name = name
        self.url = url

class Menu:
    def __init__(self, config, albums):
        self.items = []
        for elem in albums:
            self.items.append(MenuItem(elem.name, config.url + "/" + elem.name))

class Config:
    def __init__(self, name, url):
        self.name = name
        self.url = url


class Picture:
    def __init__(self, path, name, parent):
        self.path = path
        self.name = name
        self.parent = parent
        self.large = workingdir + "/output/" + self.parent.name + "/" + os.path.splitext(self.name)[0] + "_large.jpeg"
        self.html = workingdir + "/output/" + self.parent.name + "/" + os.path.splitext(self.name)[0] + ".html"
        self.small = workingdir + "/output/" + self.parent.name + "/" + os.path.splitext(self.name)[0] + "_small.jpeg"
        self.link = "/" + self.parent.name + "/" + os.path.splitext(self.name)[0] + ".html"
        self.linkSmall = "/" + self.parent.name + "/" + os.path.splitext(self.name)[0] + "_small.jpeg"
        self.linkLarge = "/" + self.parent.name + "/" + os.path.splitext(self.name)[0] + "_large.jpeg"
    def resize(self,basewidth, img):
        wpercent = (basewidth/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))       
        img = img.resize((basewidth,hsize), Image.LANCZOS)
        return img
    
    def resize_images(self):
        img = Image.open(self.path)
        imgSmall = self.resize(150, img)
        imgSmall.save(self.small, optimize=True)
        imgLarge = self.resize(600, img)
        imgLarge.save(self.large, optimize=True)
class Album:
    def __init__(self, path, name):
        self.path = path
        self.name = name
        self.html = path.replace("photos", "output") + "/index.html"
        self.description = "" #TODO
        self.pictures = []
    
    def read_children(self):
        if len(self.pictures) != 0:
            self.pictures = []
        for file in os.listdir(self.path):
            if os.path.isfile(self.path + "/" + file) and (file.lower().endswith("jpeg") or file.lower().endswith("jpg")):
                self.pictures.append(Picture(self.path + "/" + file, file, self))

def read_albums():
    albums = []
    for elem in os.listdir(workingdir + "/photos"):
        if os.path.isdir(workingdir+"/photos/"+elem):
            albums.append(Album(workingdir+"/photos/"+elem, elem))
    return albums
def read_configuration():
    f = open(workingdir + "/config.yml", "r")
    data = ''.join(f.readlines())
    data = yaml.load(data)
    return Config(data['name'], data['url'])


def validate_directory(simple=True):
    config_exists = False
    photos_exists = False
    template_exists = False
    for file in os.listdir(workingdir):
        if file == "assets":
            template_exists = True
        elif file == "config.yml":
            config_exists = True
        elif file == "photos":
            photos_exists = True
    if simple is True: 
        return config_exists and photos_exists and template_exists
    return {'config': config_exists, 'photos': photos_exists, 'template': template_exists}


def help():
    print("Help Comes Here")


def build():
    if validate_directory() is True:
        config = read_configuration()
        albums = read_albums()
        for album in albums:
            album.read_children()
        menu = Menu(config, albums)
        shutil.rmtree(workingdir + '/output', ignore_errors=True)
        os.mkdir(workingdir + '/output')
        shutil.copyfile("assets/style.css", "output/style.css") 
        for album in albums:
            os.mkdir(workingdir + '/output/' + album.name)
            with open(album.html, "w") as f:
                f.write(render_template("list.html", {'config': config, 'album': album, 'menu': menu}))
                f.close()
            for picture in album.pictures:
                picture.resize_images()
                with open(picture.html, "w") as f:
                    f.write(render_template("single.html", {'config': config, 'picture': picture, 'menu': menu}))
                    f.close()
        all = []
        for album in albums:
            for image in album.pictures:
                all.append(image)
        with open(workingdir + "/output/index.html", "w") as f:
            f.write(render_template("index.html", {'config': config, 'menu': menu, 'pictures': all}))
            f.close()
                
    else:
        print("This folder have not been initialised or something is wrong with it")


def init():
    if not validate_directory():
        directory = validate_directory(simple = False)
        if directory['config'] is False:
            with open(workingdir + '/config.yml', 'w') as f:
               f.write('name: "photos.hjertnes.blog"\nurl: "https://photo.hjertnes.blog"')
               f.close()
        if directory['photos'] is False:
            os.mkdir(workingdir + '/photos')
        if directory['template'] is False:
            os.mkdir(workingdir + '/assets')
            with open(workingdir + '/assets/style.css', 'w') as f:
                f.write('\n')
                f.close()
            with open(workingdir + '/assets/base.html', 'w') as f:
                f.write(default['base'])
                f.close()
            with open(workingdir + '/assets/single.html', 'w') as f:
                f.write(default['single'])
                f.close()
            with open(workingdir + '/assets/list.html', 'w') as f:
                f.write(default['list'])
                f.close()
            with open(workingdir + '/assets/index.html', 'w') as f:
                f.write(default['index'])
                f.close()
    else:
        print("This folder have already been initialized")


if len(sys.argv) > 1:
    command = sys.argv[1]
    if command == "help":
        help()
    elif command == "build":
        build()
    elif command == "init":
        init()
else:
    help()
