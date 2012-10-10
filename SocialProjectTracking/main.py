#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import webapp2
import jinja2
import facebook
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
    autoescape = True)

FACEBOOK_APP_ID = '531630580186665'
FACEBOOK_APP_SECRET = '4213defabc83ac566267b8c6fe337c67'
oauth_access_token = 'AAAHjgZBPiPikBAP06TmSNf6bjb3nKZArMseMZBJZAHTnHSwfCpLYUGgClcNNz3CLZAq6bNNaGj10FGKyYocoLT5y9cZAIDjGrwZCllAAaIgrAZDZD'

class User(db.Model):
    id = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    name = db.StringProperty(required=True)
    profile_url = db.StringProperty(required=True)
    access_token = db.StringProperty(required=True)

class Project(db.Model):
    name = db.StringProperty(required=True)
    author = db.ReferenceProperty(required=True)
    business = db.IntegerProperty(required=True, choices=(1,2,3))


class Purchaser(db.Model):
    user = db.ReferenceProperty(User)
    name = db.StringProperty(required=True)
    business = db.StringProperty(required=True, choices=('Heavy Industry','Software Development','IT'))


class MainHandler(webapp2.RequestHandler):
    @property
    def current_user(self):
        if not hasattr(self, "_current_user"):
            self._current_user = None
            cookie = facebook.get_user_from_cookie(
                self.request.cookies, FACEBOOK_APP_ID, FACEBOOK_APP_SECRET)
            if cookie:
                # Store a local instance of the user data so we don't need
                # a round-trip to Facebook on every request
                user = User.get_by_key_name(cookie["uid"])
                if not user:
                    graph = facebook.GraphAPI(cookie["access_token"])
                    profile = graph.get_object("me")
                    user = User(key_name=str(profile["id"]),
                                id=str(profile["id"]),
                                name=profile["name"],
                                profile_url=profile["link"],
                                access_token=cookie["access_token"])
                    user.put()

                elif user.access_token != cookie["access_token"]:
                    user.access_token = cookie["access_token"]
                    user.put()
                self._current_user = user
        return self._current_user

    def logout(self):
        self.response.headers.add_header('Set-Cookie','uid=; Path=/')

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        self.user = self.current_user

class MainPage(MainHandler):
    def get(self):
        user = self.user
        if user:
            self.redirect('/account')
        else:
            self.render('index.html', user=user)


class UserPage(MainHandler):
    def get(self):
        user = self.user
        if user:
            graph = facebook.GraphAPI(user.access_token)
            profile = graph.get_object("me")
            friends = graph.get_connections("me", "friends")
            self.render('profile.html', user=user, profile=profile)
        else:
            self.redirect('/')

    def post(self):
        user = self.user
        message = self.request.get('message')
        graph = facebook.GraphAPI(user.access_token)
        graph.put_object("me", "feed", message=message)
        self.redirect('/account')

class ProjectPage(MainHandler):
    def get(self, project_id):
        project = Project.get_by_id(int(project_id))
        project_id = project.key().id()
        self.render('project_page.html', project=project, project_id=project_id)

class LogoutPage(MainHandler):
    def get(self):
        self.logout()
        self.redirect("/")

class AddProject(MainHandler):
    def get(self):
        self.render('add_project.html')

    def post(self):
        project_name = self.request.get('name')
        project_businees = int(self.request.get('business'))
        project = Project(name=project_name, business=project_businees, author=self.user)
        project.put()
        self.redirect('/project/%d' % project.key().id())   


app = webapp2.WSGIApplication([
    ('/', MainPage), ('/logout', LogoutPage), ('/project/add', AddProject), ('/account', UserPage),
    ('/project/(\d+)/?', ProjectPage),
], debug=True)
