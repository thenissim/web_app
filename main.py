# ------------------------------------------------------
# Send Mail with Database
# ------------------------------------------------------
# The application is an interface between dog owners and walkers.
# Stores the information in the database
# ------------------------------------------------------
# Author       - Adar Nissim, Eden Lotan, Tamar Holder
# Last updated - 09.01.2021
# ------------------------------------------------------

import webapp2
from google.appengine.api import users
import jinja2
import os
import logging
import db_handler

# import the relevant classes 
import mainwalker
import mainowner


jinja_environment = jinja2.Environment(	loader=
										jinja2.FileSystemLoader(os.path.dirname(__file__)))
                                        
                                        
#-----------------------------------------------------------------
#this class is where the user chooses whether he is a dog walker or owner. it sends him to the matching log in page.
class MainPage(webapp2.RequestHandler):
    def get(self):
		template = jinja_environment.get_template('main_page.html')
		self.response.write(template.render())
                                        
#-----------------------------------------------------------------
class LoginWalker(webapp2.RequestHandler):
    def get(self):

        user = users.get_current_user()  
        # if the user object exists (the user is logged in to google)
        if user: 
            self.redirect('/main_walker')
        else:      
            # force the user to login 
            self.redirect(users.create_login_url('/main_walker'))
            
class LoginOwner(webapp2.RequestHandler):
    def get(self):

        user = users.get_current_user()  
        # if the user object exists (the user is logged in to google)
        if user: 
            self.redirect('/main_owner')
        else:      
            # force the user to login 
            self.redirect(users.create_login_url('/main_owner'))
#--------------------------------------------------------------
class Logout(webapp2.RequestHandler):
    def get(self):

        # if the user is logged in - we will perform log out
        user = users.get_current_user()

        if user:    
            # send user to logout and redirect him afterwards to main page
            self.redirect(users.create_logout_url('/main_page'))

        else:
            self.redirect('/main_page')
# -------------------------------------------------------------
class MainWalker(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        email = user.email()
        db = db_handler.DbHandler()
        db.connectToDb()
        cursor = db.getCursor()
        sql_walker_name = """SELECT Walker_Name FROM Dog_Walker WHERE Walker_Email= %s"""
        cursor.execute(sql_walker_name, [email])
        temp = cursor.fetchone()
        db.disconnectFromDb()
        if temp:
            name = temp[0]
            parameters_for_template = {'email':email,"name":name}
            template = jinja_environment.get_template('main_walker.html')
            self.response.write(template.render(parameters_for_template))
        else:
            self.redirect('/sign_up_walker')
        
        
class MainOwner(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        email = user.email()
        db = db_handler.DbHandler()
        db.connectToDb()
        cursor = db.getCursor()
        sql_walker_name = """SELECT Owner_Name FROM Owner WHERE Owner_Email= %s"""
        cursor.execute(sql_walker_name, [email])
        temp = cursor.fetchone()
        db.disconnectFromDb()
        if temp:
            name = temp[0]
            parameters_for_template = {'email':email,"name":name}
            template = jinja_environment.get_template('main_owner.html')
            self.response.write(template.render(parameters_for_template))
        else:
            self.redirect('/sign_up_owner')
# -------------------------------------------------------------


class MainErrors(webapp2.RequestHandler):
    # this class shows the user what went wrong
    def get(self):
        # Display the error message according to the one sent in the url
        error_num = self.request.get('error_type')
        if error_num == "1": #second attempt to sign up
            if self.request.get('type') == 'walker': #we need to know if the second sign up attempt came from walker or owner
                parameters_for_template = {'error_type':"You already signed up, no need to do it again. You can go back to main page.",
                                            'type':'walker',"error_num":"1"}
            else:
                parameters_for_template = {'error_type':"You already signed up, no need to do it again. You can add a new dog or go back to main page.",
                                            'type':'owner',"error_num":"1"}
        elif error_num == "2": #adding same dog
            parameters_for_template = {'error_type':"This dog has already been added, you can add a different dog or go back to main page.",
                                            'type':'owner',"error_num":"2"}
        elif error_num == "3":
            parameters_for_template = {'error_type':"You don't have any registered dogs in our system.<br>Please enter a dog before application submittal",
                                            'type':'owner',"error_num":"3"}
        elif error_num == "4":
            parameters_for_template = {'error_type':"Sorry, There are no walkers that work in your city",'type':'owner',"error_num":"4"}
        template = jinja_environment.get_template('main_errors.html')
        self.response.write(template.render(parameters_for_template))

		
		
# -------------------------------------------------------------
# Routing
# -------------------------------------------------------------
app = webapp2.WSGIApplication([	('/',  MainPage),
                                ('/main_page',  MainPage),
                                ('/main_errors', MainErrors),
                                ('/loginwalker', LoginWalker),
                                ('/main_walker', MainWalker),
                                ('/loginowner', LoginOwner),
                                ('/main_owner', MainOwner),
                                ('/sign_up_owner' , mainowner.SignUp),
                                ('/show_owner' , mainowner.ShowOwner),
                                ('/add_dog' , mainowner.AddDog),
                                ('/show_dog',mainowner.ShowDog),
                                ('/submit_walk_app',mainowner.SubmitWalkApp),
                                ('/match_walker', mainowner.MatchWalker),
                                ('/show_match', mainowner.ShowMatch),
                                ('/owner_app_interface' , mainowner.AppInterface),
                                ('/sign_up_walker' , mainwalker.SignUp),
                                ('/show_walker' , mainwalker.ShowWalker),
                                ('/walker_app_interface' , mainwalker.AppInterface),
                                ('/calendar' , mainwalker.Calendar),
                                ('/logout', Logout)],
								debug=True)