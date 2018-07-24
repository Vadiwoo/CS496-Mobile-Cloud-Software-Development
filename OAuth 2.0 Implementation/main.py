from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch
import json
import webapp2
import urllib
import random
import string
import json
import os


client_ID = "135386068742-0t8fsah657ort3alsvrqarfuicnrd4t7.apps.googleusercontent.com"
client_Secret = "q840NwaW5yMQlclwpM0OU155"
call_URL = "https://accounts.google.com/o/oauth2/v2/auth"
redirect_URL = "https://oauth-implementation-vadiwoo.appspot.com/oauth"

class OAuthHandler(webapp2.RequestHandler):
    def get(self,):
        auth_code = self.request.GET['code']
        state = self.request.GET['state']

        post_body = {
            'code': auth_code,
            'client_id': client_ID,
            'client_secret': client_Secret,
            'redirect_uri': redirect_URL,
            'grant_type': 'authorization_code'
            }

        payload = urllib.urlencode(post_body)
        headers = {'Content-Type':'application/x-www-form-urlencoded'}
        result = urlfetch.fetch(
            url="https://www.googleapis.com/oauth2/v4/token",payload = payload, method = urlfetch.POST,headers = headers)

        json_result = json.loads(result.content)

        headers = {'Authorization': 'Bearer ' + json_result['access_token']}
        result = urlfetch.fetch(
            url="https://www.googleapis.com/plus/v1/people/me",
            method = urlfetch.GET,
            headers=headers)

        json_result = json.loads(result.content)
        # self.response.write(json.dumps(json_result['name']['givenName']))
        exist_fname = False
        exist_lname = False
        exist_gplink = False
        exist_account = False
        for item in json_result:
            if item == 'name':
                if item[0]:
                    exist_fname = True
                if item[0]:
                    exist_lname = True
            if item == 'url':
                exist_gplink = True

        if exist_fname and exist_lname and exist_gplink:
            fname = json_result['name']['givenName']
            lname = json_result['name']['familyName']
            gplink = str(json_result['url'])
            exist_account = True
            template_values = {'fname': fname,
                               'lname': lname,
                               'gplink': gplink,
                               'gplink_name': "Get Access",
                               'state': state}
        else:
            template_values = {'noAccount': "No Google+ account found", 'state': state}

        path = os.path.join(os.path.dirname(__file__), 'templates/results.html')
        self.response.out.write(template.render(path, template_values))
      

class MainPage(webapp2.RequestHandler):
    def get(self):
        random_string = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(32)])

        url_linktext = 'Get Access'
    # An example URL :
    # https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id=107461084371-0vr1hjlgafvltftq307ceq0pcjrk2ad4.apps.googleusercontent.com&redirect_uri=https://osu-cs496-demo.appspot.com/oauth&scope=email&state=SuperSecret9000
        url = call_URL + "?response_type=code&client_id=" + client_ID + "&redirect_uri=https://oauth-implementation-vadiwoo.appspot.com/oauth" + "&scope=email&state=" + random_string 
        


        template_values = {'url': url}

        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        self.response.out.write(template.render(path, template_values))

                
app = webapp2.WSGIApplication([     
    ('/', MainPage),
    ('/oauth', OAuthHandler)
], debug=True)
