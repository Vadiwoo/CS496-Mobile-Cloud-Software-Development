from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import json
import webapp2
import urllib
import random
import string
import json
import os


client_ID = "4951786660808371059"
client_Secret = "150c07dd063848fd930141d6eb25e21194a13afa67d2ab1d54e9e462d646a038"
call_URL = "https://api.pinterest.com/oauth/"
#redirect_URL = "http://localhost:8080/callback" 
redirect_URL = "https://cloud-finalproject-74821.appspot.com/oauth" 

class UserAccount(ndb.Model):
    id = ndb.StringProperty()
    user_id = ndb.StringProperty()
    first_name = ndb.StringProperty(required=True)
    last_name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    is_active = ndb.BooleanProperty(default=True) #newly created user is active
    

class UserAccountHandler(webapp2.RequestHandler):
    def post(self): #create user
        user_data = json.loads(self.request.body)       
        new_user = UserAccount(user_id=user_data['user_id'],first_name=user_data['first_name'], last_name=user_data['last_name'], email=user_data['email'])
        new_user.put()
        new_user.id = str(new_user.key.urlsafe()) 
        new_user.put()
        user_dict = new_user.to_dict()
        self.response.set_status(201)
        self.response.write(json.dumps(user_dict))


    def get(self, user_id):
        user_account_exists = False
        UserAccount_key = ""
        for user in UserAccount.query():
            if user.user_id == user_id:
                user_account_exists = True
                UserAccount_key = user.id
        if user_account_exists:
            get_UserAccount = ndb.Key(urlsafe=UserAccount_key).get()
            get_UserAccount_dict = get_UserAccount.to_dict()
            get_UserAccount_dict['self'] = "/user/" + user_id + "/account"
            self.response.write(json.dumps(get_UserAccount_dict))
        else:
            self.response.status = 400
            self.response.write("User does not exist.")
    

    def patch(self, user_id):
        patch_data = json.loads(self.request.body)
        user_account_exists = False
        UserAccount_key = ""
        for user in UserAccount.query():
            if user.user_id == user_id:
                user_account_exists = True
                UserAccount_key = user.id
        if user_account_exists:
            modifyUser = ndb.Key(urlsafe=UserAccount_key).get()
            if modifyUser:
                user_data = json.loads(self.request.body)
                if 'first_name' in user_data:                   
                    modifyUser.first_name = user_data['first_name']                    
                    modifyUser.put()
                    self.response.write("User 'first_name' was updated succesfully")
                if  'last_name' in user_data:
                    modifyUser.last_name = user_data['last_name']
                    modifyUser.put()
                    self.response.write("User 'last_name' was updated succesfully")
                if 'email' in user_data:
                    modifyUser.email = user_data['email']
                    modifyUser.put()
                    self.response.write("User 'email' was updated succesfully")

                modifyUser.put()
                user_dict = modifyUser.to_dict()
                self.response.set_status(201)
                self.response.write(json.dumps(user_dict))
            else:
                self.response.set_status(404)
                self.response.write('Sorry, cannot find that user')
                return
        else:
            self.response.set_status(404)
            self.response.write('User does not exist"')   
            

    def put(self, user_id): #Put user to active status
        #put_data = json.loads(self.request.body)
        for user in UserAccount.query():
            if user.user_id == user_id:
                user_account_exists = True
                UserAccount_key = user.id
        if user_account_exists:

            putUser = ndb.Key(urlsafe=UserAccount_key).get()
            is_active = putUser.is_active

        #if 'is_active' in put_data:
        #put_user_to_active == put_data['is_active']
            if is_active:
                putUser.is_active = False
                putUser.put()
                self.response.set_status(200)
                self.response.write('User status has been changed to be  NOT active.')  
                
            else:
                putUser.is_active = True
                putUser.put()
                self.response.set_status(200)
                self.response.write('User status has been changed to be active.')  


        else:                                         
            everyUser = UserAccount.query().fetch()
            if len(everyUser) < 1: 
                self.response.set_status(404) 
                self.response.write('Sorry, there are no User available.')
            else:
                self.response.set_status(404) 
                self.response.write('Sorry, cannot find that user.')  
             


    def delete(self, user_id):
        user_account_exists = False
        UserAccount_key = ""
        for user in UserAccount.query():
            if user.user_id == user_id:
                user_account_exists = True
                UserAccount_key = user.id
        if user_account_exists:
            ndb.Key(urlsafe=UserAccount_key).delete()
            for user in Recipe.query():
                if user.user_id == user_id:
                    Recipe_key = user.id
                    ndb.Key(urlsafe=Recipe_key).delete()
            self.response.write("User's account  was succesfully deleted")
        else:
            self.response.status = 400
            self.response.write("User does not exist")


class Recipe(ndb.Model):
    id = ndb.StringProperty()
    user_id = ndb.StringProperty();
    recipe_name = ndb.StringProperty(required=True)
    recipe_type = ndb.StringProperty()
    source_url = ndb.StringProperty(required=True)
    ingredients = ndb.StringProperty()
    instructions = ndb.StringProperty()


class RecipeHandler(webapp2.RequestHandler):        
    def post(self, user_id): #create new recipe
        recipe_data = json.loads(self.request.body)
        user_exists = False
        User_key = ""
        for user in UserAccount.query():
            if user.user_id == user_id:
                user_exists = True
                User_key = user.id 
        if user_exists:
            user_status = False
            current_user= ndb.Key(urlsafe=User_key).get()
            if current_user.is_active == True:
                user_status = True
            if user_status:
                new_recipe = Recipe()
                new_recipe.user_id = user_id
                new_recipe.recipe_name = recipe_data['recipe_name']
                new_recipe.source_url= recipe_data['source_url']
                new_recipe.put()
                new_recipe.id = str(new_recipe.key.urlsafe())
                new_recipe.put()
                new_recipe_dict = new_recipe.to_dict()
                new_recipe_dict['self'] = '/user/' + new_recipe.user_id + "/recipe/" + new_recipe.id
                self.response.set_status(201)
                self.response.write(json.dumps(new_recipe_dict))
            else:
                self.response.status = 400
                self.response.write("Sorry, User account is NOT active. Cannot add recipes!")

        else:
            self.response.status = 400
            self.response.write("User does not exist")

    def get(self, user_id=None, recipe_id=None):
        user_exists = False
        for user in UserAccount.query():
            if user.user_id == user_id:
                user_exists = True
        if user_exists:
            if recipe_id:
                recipe_exists = False
                for recipe in Recipe.query():
                    if recipe.id == recipe_id:
                        recipe_exists = True
                if recipe_exists:
                    get_Recipe = ndb.Key(urlsafe=recipe_id).get()
                    get_Recipe_dict = get_Recipe.to_dict()
                    get_Recipe_dict['self'] = "/user/" + user_id + "/recipe/" + recipe_id
                    self.response.write(json.dumps(get_Recipe_dict))
                else:
                    self.response.status = 400
                    self.response.write("Recipe does not exist")
            else:
                asset_list = []
                Recipe_key = ""
                for user in Recipe.query():
                    if user.user_id == user_id:
                        Recipe_key = user.id 
                        get_Recipe = ndb.Key(urlsafe=Recipe_key).get()
                        get_Recipe_dict = get_Recipe.to_dict()
                        get_Recipe_dict['self'] = "/user/" + user_id + "/recipe/" + user.id #WHY user.id
                        asset_list.append(get_Recipe_dict)
                        
                self.response.write(json.dumps(asset_list))
        else:
            self.response.status = 400
            self.response.write("User does not exist")

 
  
            
    def delete(self, user_id, recipe_id): #Delete a recipe
        user_exists = False
        for user in UserAccount.query():
            if user.user_id == user_id:
                user_exists = True
        if user_exists:
            Recipe_exists = False
            for recipe in Recipe.query():
                if recipe.id == recipe_id:
                    Recipe_exists = True
            if Recipe_exists:
                ndb.Key(urlsafe=recipe_id).delete()
                self.response.write("Recipe was succesfully deleted")
            else:
                self.response.status = 400
                self.response.write("Recipe does not exist")
        else:
            self.response.status = 400
            self.response.write("User does not exist")
    

    def put(self, user_id, recipe_id): 
        put_data = json.loads(self.request.body)
        user_exists = False
        for user in UserAccount.query():
            if user.user_id == user_id:
                user_exists = True
        if user_exists:
            Recipe_exists = False
            for recipe in Recipe.query():
                if recipe.user_id == user_id:
                    Recipe_exists = True
            if Recipe_exists:
                put_Recipe = ndb.Key(urlsafe=recipe_id).get()
                recipe_name = False
                recipe_type = False
                ingredients= False
                instructions= False
                for item in put_data:
                    if item == "recipe_name":
                        recipe_name = True
                    if item == "recipe_type":
                        recipe_type = True
                    if item == "ingredients":
                        ingredients = True
                    if item == "instructions":
                        instructions = True
                    if recipe_name and recipe_type and ingredients and instructions:
                        put_Recipe.recipe_name = put_data['recipe_name']
                        put_Recipe.recipe_type = put_data['recipe_type']
                        put_Recipe.ingredients = put_data['ingredients']
                        put_Recipe.instructions = put_data['instructions']
                        put_Recipe.put()
                        self.response.set_status(200)
                        self.response.write("SUCCESS: Recipe 'recipe_name', 'recipe_type', 'ingredients', and 'instructions' were updated")
                    else:
                        self.response.status = 400
                        self.response.write("NOT expected format ")                                      


            else:
                self.response.status = 400
                self.response.write("Recipe does not exist")

        else:
            self.response.status = 400
            self.response.write("User does not exist")


    def patch(self, user_id, recipe_id):
        recipe_data = json.loads(self.request.body)
        user_exists = False
        modifyRecipe = False
        for user in UserAccount.query():
            if user.user_id == user_id:
                user_exists = True
        if user_exists:
            Recipe_exists = False
            for recipe in Recipe.query():
                if recipe.id == recipe_id:
                    Recipe_exists = True
            if Recipe_exists:
                modifyRecipe = ndb.Key(urlsafe=recipe_id).get()                                                        

            if modifyRecipe:
                if 'recipe_name' in recipe_data:                   
                    modifyRecipe.recipe_name = recipe_data['recipe_name']                    
                    modifyRecipe.put()
                    self.response.write("Recipe 'recipe_name' was updated succesfully")
                if  'recipe_type' in recipe_data:
                    modifyRecipe.recipe_type = recipe_data['recipe_type']
                    modifyRecipe.put()
                    self.response.write("Recipe 'recipe_type' was updated succesfully")
                if 'ingredients' in recipe_data:
                    modifyRecipe.ingredients = recipe_data['ingredients']
                    modifyRecipe.put()
                    self.response.write("Recipe 'ingredients' was updated succesfully")
                if 'instructions' in recipe_data:
                    modifyRecipe.instructions = recipe_data['instructions']
                    modifyRecipe.put()
                    self.response.write("Recipe 'instructions' was updated succesfully")
                modifyRecipe.put()
                recipe_dict = modifyRecipe.to_dict()
                self.response.set_status(201)
                self.response.write(json.dumps(recipe_dict))
            else:
                self.response.set_status(404)
                self.response.write('Sorry, cannot find that recipe')
                return
        else:
            self.response.set_status(404)
            self.response.write(' User does not exist.')   
    

class UserHandler(webapp2.RequestHandler):
    def post(self): #create user
        user_data = json.loads(self.request.body)       
        new_user = UserAccount(user_id=user_data['user_id'],first_name=user_data['first_name'], last_name=user_data['last_name'], email=user_data['email'])
        new_user.put()
        new_user.id = str(new_user.key.urlsafe()) 
        new_user.put()
        user_dict = new_user.to_dict()
        self.response.set_status(201)
        self.response.write(json.dumps(user_dict))

    def get(self, user_id): #getting user info
        user_exists = False
        for user in UserAccount.query():
            if user.user_id == user_id:
                user_exists = True
        if user_exists:
            recipe_and_account = []
            Recipe_key = ""
            for recipe in Recipe.query():
                if recipe.user_id == user_id:
                    Recipe_key = recipe.id
                    get_Recipe= ndb.Key(urlsafe=Recipe_key).get()
                    get_Recipe_dict = get_Recipe.to_dict()
                    get_Recipe_dict['self'] = "/user/" + user_id + "/recipe/" + recipe.id
                    recipe_and_account.append(get_Recipe_dict)

            UserAccount_key = ""
            for user in UserAccount.query():
                if user.user_id == user_id:
                    UserAccount_key = user.id

            get_UserAccount = ndb.Key(urlsafe=UserAccount_key).get()
            get_UserAccount_dict = get_UserAccount.to_dict()
            recipe_and_account.append(get_UserAccount_dict)

            self_string = "/user/" + user_id
            self_dict = {"self": self_string}
            recipe_and_account.append(self_dict)
            self.response.write(json.dumps(recipe_and_account))
        else:
            self.response.status = 400
            self.response.write("User does not exist")       



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
        result = urlfetch.fetch(url="https://api.pinterest.com/v1/oauth/token",payload = payload, method = urlfetch.POST,headers = headers)

        json_result = json.loads(result.content)

        token = json_result['access_token']
        template_values = {'accessToken' : token}
        
   
    
        path = os.path.join(os.path.dirname(__file__), 'templates/results.html')
        self.response.out.write(template.render(path, template_values))
      
        

class MainPage(webapp2.RequestHandler):
    def get(self):
        random_string = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(32)])

        url_linktext = 'Get Access'
    # An example URL :
    # https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id=107461084371-0vr1hjlgafvltftq307ceq0pcjrk2ad4.apps.googleusercontent.com&redirect_uri=https://osu-cs496-demo.appspot.com/oauth&scope=email&state=SuperSecret9000
        url = call_URL + "?response_type=code&client_id=" + client_ID + "&redirect_uri=https://cloud-finalproject-74821.appspot.com/oauth" + "&scope=read_public,write_public&state=" + random_string 
        
        template_values = {'url': url}

        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        self.response.out.write(template.render(path, template_values))
        
allowed_methods = webapp2.WSGIApplication.allowed_methods          
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods
                
app = webapp2.WSGIApplication([     
    ('/', MainPage),
    ('/oauth', OAuthHandler),
    ('/user/(.*)/recipe/(.*)',RecipeHandler),
    ('/user/(.*)/recipe', RecipeHandler),
    ('/user/(.*)/account', UserAccountHandler),
    ('/user/(.*)', UserHandler),
    ('/user', UserHandler),

], debug=True)
