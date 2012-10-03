#!/usr/bin/env python2.5
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import views
import view_metalink

application = webapp.WSGIApplication(
                                     [
                                      ('/', views.Home),
                                      ('/search/', views.Search),
                                      ('/about/', views.Template),
                                      ('/help/.*', views.Template),
                                      ('/add/', views.Add),
                                      ('/latest/', views.Latest),
                                      ('/metalink/.*', view_metalink.Metalink),
                                      ('/tasks/validate', views.Validate),
                                      ('/tasks/janitor', views.Janitor),
                                      ('/robots.txt', views.RobotsTXT),
                                     ],
                                     debug = True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
