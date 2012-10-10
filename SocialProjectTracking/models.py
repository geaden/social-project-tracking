#-*- coding:utf-8 -*-
from google.appengine.ext import db

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


