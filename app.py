#!/usr/bin/env python
from credentials import api_token, dev_key, ytkanan_token, ythonest_token, ytabhinav_token
import webapp2,urllib,urllib2,json,jinja2,os,datetime
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.tools import argparser

DEVELOPER_KEY = dev_key
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

#contains links already tubed
class AlreadyTubed(db.Expando):
    url = db.StringProperty()

class Cron(webapp2.RequestHandler):
    def send_yo(self, token=api_token):
        data = {'api_token':token}
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

    def get_tube(self):
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
        self.get_kanan(youtube)
        self.get_honest(youtube)
        return self.get_abhinav(youtube)

    def get_honest(self, youtube):
        newest_video = self.get_playlist(youtube, 'PL86F4D497FD3CACCE')

        already_tubed = [instance.url for instance in AlreadyTubed.all().fetch(1000000)]

        if newest_video not in already_tubed:
           self.add_to_db(newest_video)
           self.send_yo(ythonest_token)
           return newest_video

        return already_tubed

    def get_kanan(self, youtube):
        newest_video = self.get_user(youtube, 'knngill')
        already_tubed = [instance.url for instance in AlreadyTubed.all().fetch(1000000)]

        if newest_video not in already_tubed:
            self.add_to_db(newest_video)
            self.send_yo(ytkanan_token)
            return newest_video

        return already_tubed

    def get_abhinav(self, youtube):
        newest_video = self.get_user(youtube, 'linkinparkreigns')
        already_tubed = [instance.url for instance in AlreadyTubed.all().fetch(1000000)]

        if newest_video not in already_tubed:
            self.add_to_db(newest_video)
            self.send_yo(ytabhinav_token)
            return newest_video

        return already_tubed

    def get_user(self, youtube, user):
        channels_response = youtube.channels().list(
            part='contentDetails', 
            forUsername=user
        ).execute()['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        playlistitems_response = youtube.playlistItems().list(
            playlistId=channels_response,
            part='id',
            maxResults=1
        ).execute()

        newest_video = playlistitems_response['items'][0]['id']
        return newest_video

    def get_playlist(self, youtube, playlist):
        playlistitems_response = youtube.playlistItems().list(
            part='contentDetails', 
            playlistId=playlist,
            maxResults=1
        ).execute()

        newest_video = playlistitems_response['items'][0]['id']
        return newest_video

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