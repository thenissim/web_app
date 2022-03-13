import db_handler
import webapp2
from google.appengine.api import users
import jinja2
import os
import logging
import MySQLdb

jinja_environment = jinja2.Environment(	loader=
										jinja2.FileSystemLoader(os.path.dirname(__file__)))
                                        
#we will use this function every time the owner chooses an option that requiers him to sign up prior to it. 
#if he didn't, it will redirect him to sign up page no matter what he pressed.                                
def check(self):
    user = users.get_current_user()
    email = user.email()
    db = db_handler.DbHandler()
    db.connectToDb()
    cursor = db.getCursor()
    #we want to check if this owner has already signed up to the system. if the count has zero - he was not.
    sql_string = """SELECT COUNT(Owner_Email) FROM Owner WHERE Owner_Email= %s"""
    cursor.execute(sql_string, [email])
    #email_check is a list containing one tuple with the value 1- if the email was in the system, 0- otherwise.
    db.disconnectFromDb()
    return cursor.fetchone()
        
        
class SignUp(webapp2.RequestHandler):
    def get(self):
        email_check = check(self)
        if int(email_check[0]) == 1:
        #user has already signed up, no need to sign up again, so we redirect him to main owner.
            self.redirect('/main_errors?error_type=1&type=owner')
        else:
        #user's first sign up
            template = jinja_environment.get_template('sign_up_owner.html')
            self.response.write(template.render())
        

class ShowOwner( webapp2.RequestHandler):      
    def post(self):
        #the email wasnt given in the sign up, but in the login.
        user = users.get_current_user()
        email = user.email()
        #retrieving owner's information from the sign up sheet
        owner_name = self.request.get('owner_name').lower()
        owner_birthdate = self.request.get('owner_birthdate')
        owner_phone = self.request.get('owner_phone')
        owner_city = self.request.get('owner_city').lower()
        db = db_handler.DbHandler()
        db.connectToDb()
        cursor = db.getCursor()
        sql = """INSERT INTO Owner(Owner_Email,Owner_Name,Owner_Birthdate,Owner_Phone,Owner_City) VALUES (%s,%s,%s,%s,%s)"""
        #inserting into Owner table in db
        cursor.execute(sql,[email,owner_name,owner_birthdate,owner_phone,owner_city])
        db.commit()
        db.disconnectFromDb()
        template = jinja_environment.get_template('show_owner.html')
        parameters_for_template = {"Email":email,"Name":owner_name,"Birthdate":owner_birthdate,"Phone":owner_phone,"City":owner_city}
        self.response.write(template.render(parameters_for_template))
        
class AddDog( webapp2.RequestHandler):  
    def get(self):
        email_check = check(self)
        if int(email_check[0]) == 1:
        #user has already signed up, no need to sign up again, so we redirect him to add dog.
            template = jinja_environment.get_template('add_dog.html')
            self.response.write(template.render())
        else:
        #user can't add a dog before signing up
            self.redirect('/sign_up_owner')
        
        
            
class ShowDog(webapp2.RequestHandler):      
    def post(self):
        #the email wasnt given in the sign up, but in the login.
        user = users.get_current_user()
        email = user.email()
        #retrieving dog's information from the add dog sheet
        dog_name = self.request.get('dog_name').lower()
        dog_birthyear = self.request.get('dog_birthyear')
        dog_size = self.request.get('dog_size')
        gender = self.request.get('gender')
        is_friendly = self.request.get('is_friendly')
        is_vaccined = self.request.get('is_vaccined')
        db = db_handler.DbHandler()
        db.connectToDb()
        cursor = db.getCursor()
        #inserting into Owner table in db, first we check if the owner has already added this particular dog
        sql_check = """ SELECT COUNT(Dog_Name) FROM Dog WHERE Owner_Email = %s AND Dog_Name = %s """
        cursor.execute(sql_check,[email,dog_name])
        dog_check = cursor.fetchone()
        if int(dog_check[0]) == 0:
            #this is the first time the owner is entering this dog, so we add him
            sql = """INSERT INTO Dog(Dog_Name,Birth_Year,Size,Gender,Is_Friendly,Is_Vaccined,Owner_Email) VALUES (%s,%s,%s,%s,%s,%s,%s)"""
            cursor.execute(sql,[dog_name,dog_birthyear,dog_size,gender,is_friendly,is_vaccined,email])
            db.commit()
            db.disconnectFromDb()
            template = jinja_environment.get_template('show_dog.html')
            parameters_for_template = {"dog_name":dog_name,"dog_birthyear":dog_birthyear,"dog_size":dog_size,"gender":gender,"is_friendly":is_friendly,
                                        "is_vaccined":is_vaccined}
            self.response.write(template.render(parameters_for_template)) 
        else:
            #the dog is already in this owner's list of dogs.
            self.redirect('/main_errors?error_type=2&type=owner')
        #error type 1 means dog owner is trying to add the same dog
        
class SubmitWalkApp (webapp2.RequestHandler):
    def get(self):
        email_check = check(self)
        if int(email_check[0]) == 1:
        #user has already signed up, no need to sign up again, so we send him to the requested walk application page.
            user = users.get_current_user()
            email = user.email()
            db = db_handler.DbHandler()
            db.connectToDb()
            cursor = db.getCursor()
            sql_dog_name = """SELECT Dog_Name FROM Dog WHERE Owner_Email = %s """
            cursor.execute(sql_dog_name,[email])
            dog_list = cursor.fetchall() #this is a list containing owner's dogs. if it's empty- he hasn't entered any dogs.
            db.disconnectFromDb()
            num_of_dogs = len(dog_list)
            if num_of_dogs == 0: #owner has no dogs, send him to error page
                self.redirect('/main_errors?error_type=3&type=owner')
            else: #owner has one or more dogs, send him to application page
                parameters_for_template = {'dog_list':dog_list,'num_of_dogs':num_of_dogs} 
                template = jinja_environment.get_template('submit_walk_app.html')
                self.response.write(template.render(parameters_for_template))
        else:
        #user hadn't sign up yet so we just send him to sign up page   
            self.redirect('/sign_up_owner')
            
class MatchWalker (webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        email = user.email()
        chosen_dog = self.request.get('dog')
        logging.info(chosen_dog)
        #retrieving requested walks
        requested_walks = []        
        days = ["sunday","monday","tuesday","wednesday","thursday","friday","saturday"]
        shifts = ["morning","afternoon","evening"]
        for day in days:
            for shift in shifts:
                if self.request.get( day + "_" + shift ) == "available":
                        requested_walks.append((day,shift))
        db = db_handler.DbHandler()
        db.connectToDb()
        cursor = db.getCursor()
        sql_city = """SELECT Owner_City FROM Owner WHERE Owner_Email=%s"""
        cursor.execute(sql_city,[email])
        owner_city = cursor.fetchone()[0]
        sql_walkers_in_owner_city = """SELECT COUNT(*) FROM Dog_Walker
                                        WHERE Walker_City=%s; """
        cursor.execute(sql_walkers_in_owner_city,[owner_city])
        check_walkers_in_city = cursor.fetchone()[0] #if this returns 0 there are no walkers in the chosen city, disregarding requested shifts
        if int(check_walkers_in_city) == 0: 
            self.redirect('/main_errors?error_type=4&type=owner')
        sql_dog_size = """SELECT Size,Dog_ID FROM Dog WHERE Owner_Email=%s AND Dog_Name=%s"""
        cursor.execute(sql_dog_size,[email,chosen_dog])
        dog_details = cursor.fetchone()
        dog_size = dog_details[0]
        dog_id = dog_details[1]
        logging.info(dog_size)
        sql_walker_city = """SELECT Day,Shift,a.Walker_Email,Walker_Name,Price,Walker_Phone FROM Available_Shifts AS a,Dog_Walker AS dw, Price_List AS pl
                                WHERE Walker_city = %s AND a.Walker_Email=dw.Walker_Email
                                AND pl.Walker_Email = dw.Walker_Email
                                AND Dog_size = %s
                                ORDER BY FIELD(day, 'sunday','monday','tuesday','wednesday','thursday','friday','saturday'),
                                FIELD(shift,'morning','afternoon','evening' ) """
        cursor.execute(sql_walker_city,[owner_city,dog_size])
        walkers_in_city = cursor.fetchall() #this is a list containing walkers who walk in the relevant owner's city.
        logging.info(walkers_in_city)
        relevant_walkers = [] #each item in this list will be a tuple containing day,shift,walker relevant to one of the requested walks.
        duplicate = [] #this list will contain the day&shift&dog combinations that have already been submitted.
        num_of_duplicate = 0
        good_walks = []
        for requested in requested_walks:
            #we want to block multiple requests for the same dog,day,shift combination unless the request was already declined or cancelled. 
            sql_check = """SELECT COUNT(*) FROM Walk_App
                                WHERE Day_Requested=%s AND Shift_Requested=%s AND Dog_ID=%s 
                                AND Owner_Email=%s AND Status<>'declined' AND Status<>'cancelled'"""
            cursor.execute(sql_check,[requested[0],requested[1],dog_id,email]) 
            check = cursor.fetchone()[0]
            logging.info(check)
            if int(check) == 0: #this is the first time submitting this specific request, we want it in the list of good walks 
                good_walks.append(requested)
            else:
                duplicate.append([requested[0],requested[1]])
        num_of_duplicate = len(duplicate)       
        logging.info(good_walks)
        for walker in walkers_in_city:
            if (walker[0],walker[1]) in good_walks:
                relevant_walkers.append(walker)    
        logging.info(duplicate)
        db.disconnectFromDb()
        len_of_rw = len(relevant_walkers)
        exist_shift = 1
        if len_of_rw == 0: 
        #we use this to know to handle the end case where there are no available walkers in the city for the requested shifts.
            exist_shift = 0
        logging.info(len_of_rw)
        logging.info(exist_shift)
        parameters_for_template = {"chosen_dog":chosen_dog,"requested_walks":good_walks,"dog_size":dog_size,
                                    "owner_city":owner_city,"relevant_walkers":relevant_walkers,"len":len_of_rw,"exist_shift":exist_shift,
                                    "duplicate":duplicate,"num_of_duplicate":num_of_duplicate}
        template = jinja_environment.get_template('match_walker.html')
        self.response.write(template.render(parameters_for_template))
    
class ShowMatch (webapp2.RequestHandler):    
    def post(self):
        user = users.get_current_user()
        email = user.email()
        dog = self.request.get('dog_name')
        db = db_handler.DbHandler()
        db.connectToDb()
        cursor = db.getCursor()
        sql_dog_id = """SELECT Dog_ID,Size FROM Dog WHERE Dog_Name = %s """
        cursor.execute(sql_dog_id,[dog])
        dog_details = cursor.fetchone()
        dog_id = dog_details[0]
        dog_size = dog_details[1]
        days = ["sunday","monday","tuesday","wednesday","thursday","friday","saturday"]
        shifts = ["morning","afternoon","evening"]
        requests_sent = [] #a list containing information of every requested&matched walk application
        for day in days: #retrieving the information from the owner's walker choice html page
            for shift in shifts:               
                walker_email = self.request.get(day + "_" + shift)
                if walker_email: #an email was found
                    sql_insert_app = """INSERT INTO Walk_App(Day_Requested,Shift_Requested,Submit_Date,Status,Dog_ID,Walker_Email,Owner_Email)
                                        VALUES (%s,%s,curdate(),"pending",%s,%s,%s)"""
                    cursor.execute(sql_insert_app,[day,shift,dog_id,walker_email,email])
                    db.commit()
                    sql_price = """SELECT Price FROM Price_List WHERE Walker_Email = %s AND Dog_Size = %s"""
                    cursor.execute(sql_price,[walker_email,dog_size])
                    price = cursor.fetchone()[0]
                    sql_phone = """SELECT Walker_Phone,Walker_Name FROM Dog_Walker WHERE Walker_Email = %s"""
                    cursor.execute(sql_phone,[walker_email])
                    walker_details = cursor.fetchone()
                    walker_name = walker_details[1]
                    walker_phone = walker_details[0]
                    walk_request = [day,shift,walker_name,walker_email,walker_phone,price] #all the information per a singular walk
                    requests_sent.append(walk_request)
        db.disconnectFromDb()
        parameters_for_template = {"requests_sent":requests_sent,"dog_name":dog}
        template = jinja_environment.get_template('show_match.html')
        self.response.write(template.render(parameters_for_template))
    
class AppInterface (webapp2.RequestHandler):    
    def get(self):
        email_check = check(self)
        if int(email_check[0]) == 1:
        #user has already signed up, no need to sign up again, so we send him to the requested application interface page.
            user = users.get_current_user()
            email = user.email()
            db = db_handler.DbHandler()
            db.connectToDb()
            cursor = db.getCursor()
            sql_application_retrival = """SELECT Day_Requested, Shift_Requested, Submit_Date, Walker_Name, Walker_Phone, wa.Walker_Email, Dog_Name, status, App_Id
                                            FROM Walk_App AS wa 
                                            JOIN Dog_Walker AS w ON w.Walker_Email=wa.Walker_Email
                                            JOIN Dog AS d ON d.Dog_ID=wa.Dog_ID
                                            WHERE wa.Owner_Email = %s
                                            AND status<>"cancelled"
                                            ORDER BY FIELD(day_requested, 'sunday','monday','tuesday','wednesday','thursday','friday','saturday'),
                                            FIELD(shift_requested,'morning','afternoon','evening' ), Submit_Date DESC;  """
            cursor.execute(sql_application_retrival,[email]) 
            walk_application = cursor.fetchall() #this is a list containing tuples. each tuple is a walk app w/ status pending,approved,declined
            num_of_apps = len(walk_application)
            parameters_for_template = {"walk_application":walk_application,"num_of_apps":num_of_apps}
            template = jinja_environment.get_template('owner_app_interface.html')
            self.response.write(template.render(parameters_for_template))
        else:
        #user hadn't sign up yet so we just send him to sign up page   
            self.redirect('/sign_up_owner')
    
    def post(self):
        user = users.get_current_user()
        email = user.email()
        db = db_handler.DbHandler()
        db.connectToDb()
        cursor = db.getCursor()
        sql_app = """SELECT Day_Requested, Shift_Requested, Submit_Date, Walker_Name, Walker_Phone, wa.Walker_Email, Dog_Name, status, App_Id
                     FROM Walk_App AS wa 
                     JOIN Dog_Walker AS w ON w.Walker_Email=wa.Walker_Email
                     JOIN Dog AS d ON d.Dog_ID=wa.Dog_ID
                     WHERE wa.Owner_Email = %s
                     AND status<>"cancelled"
                     ORDER BY FIELD(day_requested, 'sunday','monday','tuesday','wednesday','thursday','friday','saturday'),
                     FIELD(shift_requested,'morning','afternoon','evening' ), Submit_Date DESC;  """
        cursor.execute(sql_app,[email])
        existing_apps = cursor.fetchall() 
        updated_apps = []
        for app in existing_apps:
            logging.info(app)
            logging.info(app[8])
            response = self.request.get(str(app[8]))
            if response: #the owner pressed cancel
                sql_update_response = """UPDATE Walk_App SET Status = %s, Cancellation_Date=curdate()
                                         WHERE App_ID=%s"""
                cursor.execute(sql_update_response,[response,app[8]])
                db.commit()
            #when the if doesn't happen the walker didn't respond to the application
            else:
                updated_apps.append(app) #this will be the updated existing applications/walks 
        db.disconnectFromDb()
        parameters_for_template = {"walk_application":updated_apps}
        template = jinja_environment.get_template('owner_app_interface.html')
        self.response.write(template.render(parameters_for_template))
    
    