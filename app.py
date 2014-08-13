#!/usr/bin/env python
from credentials import api_token
import webapp2,urllib,urllib2,json,jinja2,os,datetime
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.tools import argparser

DEVELOPER_KEY = "AIzaSyBU9eMQ1xW0NNEGprJIR5wgaQdrTFn_Fdc"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

#contains links already tubed
class AlreadyTubed(db.Expando):
    url = db.StringProperty()

class Cron(webapp2.RequestHandler):
    def send_yo(self):
        data = {'api_token':api_token}
        data = urllib.urlencode(data)
        request_object = urllib2.Request('http://api.justyo.co/yoall/', data)
        response = urllib2.urlopen(request_object)
        print response.read()

    def add_to_db(self,url):
        instance = AlreadyTubed()
        instance.url = url
        instance.put()

    def get(self):
        youtube_response = self.get_tube()

        youtube_response = youtube_response

        template_values = {
            'response': youtube_response
        }

        path = os.path.join(os.path.dirname(__file__), 'templates/yotube.html')
        self.response.out.write(template.render(path, template_values))

    def get_hn(self):
        hn_url = 'http://hnify.herokuapp.com/get/top'
        response = json.loads(urllib2.urlopen(hn_url).read())
        top = [i for i in response['stories'] if i['points'] > 500][0]
        if top:
            print top['link']
            already_yoyed = [instance.url for instance in AlreadyYoyed.all().fetch(1000000)]
            print already_yoyed
            if top['link'] not in already_yoyed:
                self.add_to_db(top['link'])
                self.send_yo()

    def get_tube(self):
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

        channels_response = youtube.channels().list(
            part='contentDetails', 
            forUsername='linkinparkreigns'
        ).execute()['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        playlistitems_response = youtube.playlistItems().list(
            playlistId=channels_response,
            part='id',
            maxResults=1
        ).execute()['items'][0]['id']

        already_tubed = [instance.url for instance in AlreadyTubed.all().fetch(1000000)]

        if playlistitems_response not in already_tubed:
            self.add_to_db(playlistitems_response)
            self.send_yo()
            return playlistitems_response

        return already_tubed


class Index(webapp2.RequestHandler):
    def get(self):
        template_values = {
        }

        path = os.path.join(os.path.dirname(__file__), 'templates/main.html')
        self.response.out.write(template.render(path, template_values))
            
application = webapp2.WSGIApplication([
    ('/cron', Cron),
    ('/', Index)
    ],debug=True)