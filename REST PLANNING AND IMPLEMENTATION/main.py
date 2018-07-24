from google.appengine.ext import ndb
import webapp2
import json

class Boat(ndb.Model):
    id = ndb.StringProperty() 
    name = ndb.StringProperty() 
    type = ndb.StringProperty() 
    length = ndb.IntegerProperty() 
    at_sea = ndb.BooleanProperty(default=True) #newly created boat at sea


class BoatHandler(webapp2.RequestHandler):          
    def post(self): #create boat
        boat_data = json.loads(self.request.body)       
        new_boat = Boat(name=boat_data['name'], type=boat_data['type'], length=boat_data['length'])
        new_boat.put()
        new_boat.id = new_boat.key.urlsafe()
        new_boat.put()
        boat_dict = new_boat.to_dict()
        self.response.set_status(201)
        self.response.write(json.dumps(boat_dict))

    def get(self, id=None): 
        if id: #view specific boat
            try:
                getBoat = ndb.Key(urlsafe=id).get()
                self.response.set_status(200)
                self.response.write(getBoat)
            except:
                self.response.set_status(404)
                self.response.write('Sorry, There is no boat with this id.')
        else: #view all boats
            self.response.set_status(200)
            everyBoat = Boat.query().fetch()
            for b in everyBoat:
                boat_dict = b.to_dict()
                self.response.write(json.dumps(boat_dict))  

    def put(self, id): #Put boat to sea
        try:
            putBoat = ndb.Key(urlsafe=id).get() 
            at_sea = putBoat.at_sea     #Check if boat is already at sea
            if at_sea:
                self.response.write('Boat is already at sea. Cannot assign boat to sea again!')
            else:
                putBoat.at_sea = True       #put boat at sea 
                putBoat.put()
                slip = Slip.query(Slip.current_boat == putBoat.id).get() #find the slip and update the slip
                slip.current_boat = None
                slip.arrival_date = None
                slip.put()
                self.response.write('Boat now at sea and slip is empty.')
        except:                                         
            everyBoat = Boat.query().fetch()
            if len(everyBoat) < 1: 
                self.response.set_status(404) 
                self.response.write('Sorry, there are no boats available.')
            else:
                self.response.set_status(404) 
                self.response.write('Sorry, cannot find that boat.')
    
    def delete(self, id): #Delete a boat
        try: 
            deleteBoat = ndb.Key(urlsafe=id).get()
            at_sea = deleteBoat.at_sea
            if at_sea == False:             #If the boat is in a slip, need to update  slip's arrival date and current boat status
                slip = Slip.query(Slip.current_boat == deleteBoat.id).get()
                slip.current_boat = None
                slip.arrival_date = None
                slip.put()
            deleteBoat.key.delete()
            self.response.set_status(200)
            self.response.write('Deleted boat.')
        except:
            everyBoat = Boat.query().fetch()
            if len(everyBoat) < 1: 
                self.response.set_status(404) 
                self.response.write('Sorry, there are no boats available.')
            else:
                self.response.set_status(404)
                self.response.write('Sorry, cannot find that boat.')
    
    def patch(self, id):                                                        
        if id:                                                                       
            modifyBoat = ndb.Key(urlsafe=id).get()
            if modifyBoat:
                boat_data = json.loads(self.request.body)
                if 'name' in boat_data:                   
                    modifyBoat.name = boat_data['name']                    # modify the appropriate data of a boat
                    modifyBoat.put()
                    self.response.write("Boat 'name' was updated succesfully")
                if  'type' in boat_data:
                    modifyBoat.type = boat_data['type']
                    modifyBoat.put()
                    self.response.write("Boat 'type' was updated succesfully")
                if 'length' in boat_data:
                    modifyBoat.length = boat_data['length']
                    modifyBoat.put()
                    self.response.write("Boat 'length' was updated succesfully")
                modifyBoat.put()
                boat_dict = modifyBoat.to_dict()
                self.response.set_status(201)
                self.response.write(json.dumps(boat_dict))
            else:
                self.response.set_status(404)
                self.response.write('Sorry, cannot find that boat')
                return
        else:
            self.response.set_status(404)
            self.response.write('Please include id of boat.')   

class Slip(ndb.Model):
    id = ndb.StringProperty() 
    number = ndb.IntegerProperty() 
    current_boat = ndb.StringProperty(default=None) 
    arrival_date = ndb.StringProperty(default=None) 

    
class SlipHandler(webapp2.RequestHandler):         
    def post(self):  #create a new slip
        slip_data = json.loads(self.request.body) 
        new_slip = Slip(number=slip_data['number'])
        new_slip.put()
        new_slip.id = new_slip.key.urlsafe()
        new_slip.put()
        slip_dict = new_slip.to_dict()
        self.response.set_status(201)
        self.response.write(json.dumps(slip_dict))
        
        
    def get(self, id=None):
        if id: # view a specific slip
            slip = ndb.Key(urlsafe=id).get()
            self.response.write(slip)
            self.response.set_status(200)
        else: #view all slips
            self.response.set_status(200)
            everySlip = Slip.query().fetch()
            for s in everySlip:
               self.response.write(s)

    def delete(self, id): #Delete a slip     
            try:
                delSlip = ndb.Key(urlsafe=id).get()
                slipBoat = delSlip.current_boat
                if slipBoat:                        #If a boat is in a slip, remove the boat before deleting
                    boat = Boat.query(Boat.id == slipBoat).get()    
                    boat.at_sea = True #put the boat at sea
                    boat.put()
                    self.response.write('Put boat to sea.')     
                    self.response.write('\n')
                    self.response.write('\n')
                delSlip.key.delete()
                self.response.write('Deleted slip.')
            except:
                everySlip = Slip.query().fetch()
                if len(everySlip) < 1: 
                    self.response.set_status(404) 
                    self.response.write('Sorry, there are no slips to delete.')
                else:
                    self.response.set_status(404) 
                    self.response.write('Sorry, cannot find that slip.')
            
    def patch(self, id):        #Modify a slip. 
        if id:
            modSlip = ndb.Key(urlsafe=id).get()
            if modSlip:
                slip_data = json.loads(self.request.body)
                if 'number' in slip_data:                    
                    modSlip.number = slip_data['number']                    
                if  'arrival_date' in slip_data:
                    modSlip.type = slip_data['arrival_date']                
                modSlip.put()
                slip_dict = modSlip.to_dict()
                self.response.set_status(201)
                self.response.write(json.dumps(slip_dict))
            else:
                self.response.set_status(404)
                self.response.write('Sorry, cannot find that slip.')
                return
        else:
            self.response.set_status(404)
            self.response.write('Please include id of slip.')
            
    def put(self, id): #assign boat to slip
        slip = ndb.Key(urlsafe=id).get()
        if slip.current_boat:                   #If slip is occupied, set to  403 Forbidden error
            self.response.set_status(403)
            self.response.write('Slip already occupied.')
            return
        try:
            slip = ndb.Key(urlsafe=id).get()
            slip_data = json.loads(self.request.body)
            boat = Boat.query(Boat.id == slip_data['current_boat']).get()   #Get the boat specified by the request body
            if boat.at_sea == False: 
                self.response.write('Boat already in a slip.')     
            else:                
                slip.current_boat = slip_data['current_boat']   #Update the slip's boat and arrival date
                slip.arrival_date = slip_data['arrival_date']
                slip.put()
                boat.at_sea = False         #set the at_sea value to false
                boat.put()
                self.response.write('Put boat in slip.')                
        except:
            everySlip = Slip.query().fetch()
            everyBoat = Boat.query().fetch()            
            if len(everySlip) < 1: 
                self.response.set_status(404) 
                self.response.write('Sorry, there are no slips available.')
            elif len(everyBoat) < 1:
                self.response.set_status(404) 
                self.response.write('Sorry, there are no boats available.')
            else:
                self.response.set_status(404) 
                if slip == None:
                    self.response.write('No slip.')
                if boat == None:
                    self.response.write('No boat.')



class MainPage(webapp2.RequestHandler):             #The main page
    def get(self):
        self.response.write('REST Planning and Implementation')
        
allowed_methods = webapp2.WSGIApplication.allowed_methods          
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods
app = webapp2.WSGIApplication([        
    ('/', MainPage),
     ('/boat', BoatHandler),
    ('/boat/(.*)', BoatHandler),
    ('/slip', SlipHandler),
    ('/slip/(.*)', SlipHandler)

   
], debug=True)
