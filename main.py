# -*- coding: utf-8 -*-


import os

import webapp2
import jinja2

import pyirclogs

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class MainPage(webapp2.RequestHandler):
    def get(self):
        path = './logs' + self.request.path
        b = os.path.exists(path)
        os.makedirs([])

        template_values = {}

        self.response.out.write('<html><body>%s: %s</body></html>' % (path, str(b)))
        #template = jinja_environment.get_template('templates/DirPage.html')
        #self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([('/.*', MainPage)],
                              debug=True)