import db_handler
import webapp2
from google.appengine.api import users
import jinja2
import os
import logging
import MySQLdb
from datetime import datetime

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
    sql_string = """SELECT COUNT(Walker_Email) FROM Dog_Walker WHERE Walker_Email= %s"""
    cursor.execute(sql_string, [email])
    #email_check is a list containing one tuple with the value 1- if the email was in the system, 0- otherwise.
    db.disconnectFromDb()
    return cursor.fetchone()
        
        
class SignUp(webapp2.RequestHandler):
    def get(self):
        email_check = check(self)
        if int(email_check[0]) == 1:
        #user has already signed up, no need to sign up again, so we redirect him to main owner.
            self.redirect('/main_errors?error_type=1&type=walker')
        else:
        #user's first sign up
            template = jinja_environment.get_template('sign_up_walker.html')
            self.response.write(template.render())
        

class ShowWalker( webapp2.RequestHandler):      
    def post(self):
        #the email wasnt given in the sign up, but in the login.
        user = users.get_current_user()
        email = user.email()
        #retrieving owner's information from the sign up sheet
        walker_name = self.request.get('walker_name').lower()
        walker_birthdate = self.request.get('walker_birthdate')
        walker_phone = self.request.get('walker_phone')
        walker_city = self.request.get('walker_city').lower()
        walker_address = self.request.get('walker_address').lower()
        first_year = self.request.get('first_year')
        db = db_handler.DbHandler()
        db.connectToDb()
        cursor = db.getCursor()
        sql = """INSERT INTO Dog_Walker(Walker_Email,Address,Walker_Name,Walker_Phone,Walker_City,Walker_Birthdate,First_Year,Monthly_Fee,Reg_Date) VALUES (%s,%s,%s,%s,%s,%s,%s,0,curdate())"""
        #inserting into Owner table in db
        cursor.execute(sql,[email,walker_address,walker_name,walker_phone,walker_city,walker_birthdate,first_year])
        db.commit()
        #retrieving available shifts
        available_shifts = []        
        days = ["sunday","monday","tuesday","wednesday","thursday","friday","saturday"]
        shifts = ["morning","afternoon","evening"]
        for day in days:
            for shift in shifts:
                if self.request.get( day + "_" + shift ) == "available":
                        available_shifts.append((day,shift))
        for shift in available_shifts:
            sql2 = """INSERT INTO Available_Shifts(Day,Shift,Walker_Email) VALUES (%s,%s,%s)"""
            cursor.execute(sql2,[shift[0],shift[1],email])
            db.commit()
        s_price = self.request.get('s_price')
        m_price = self.request.get('m_price')
        l_price = self.request.get('l_price')
        price_for_size = [("small",s_price),("medium",m_price),("large",l_price)]
        for i in range(0,3):
            sql3 = """INSERT INTO Price_List(Dog_Size,Price,Walker_Email) VALUES (%s,%s,%s)"""
            cursor.execute(sql3,[price_for_size[i][0],price_for_size[i][1],email])
            db.commit()
        db.disconnectFromDb()
        template = jinja_environment.get_template('show_walker.html')
        curr_year = int(datetime.now().year) - int(first_year)
        parameters_for_template = {"Email":email,"Name":walker_name,"Birthdate":walker_birthdate,"Phone":walker_phone,"City":walker_city,
                                    "Address":walker_address,"Experience":curr_year,"available_shifts":available_shifts,"price_for_size":price_for_size}
        self.response.write(template.render(parameters_for_template))
        
               
class AppInterface( webapp2.RequestHandler):      
    def get(self):
        email_check = check(self)
        if int(email_check[0]) == 1:
        #user has already signed up, no need to sign up again, so we send him to requested page to view his applications.
            user = users.get_current_user()
            email = user.email()
            db = db_handler.DbHandler()
            db.connectToDb()
            cursor = db.getCursor()
            sql_app = """SELECT Day_Requested, Shift_Requested, Submit_Date, Owner_Name, Owner_Phone, wa.Owner_email, Size, App_ID
                            FROM Walk_App AS wa 
                            JOIN Owner AS o ON o.Owner_Email=wa.Owner_Email
                            JOIN Dog AS d ON d.Dog_ID=wa.Dog_ID
                            WHERE wa.Walker_Email=%s AND Status="pending"
                            ORDER BY FIELD(day_requested, 'sunday','monday','tuesday','wednesday','thursday','friday','saturday'),
                                  FIELD(shift_requested,'morning','afternoon','evening' ); """
            cursor.execute(sql_app,[email])
            existing_apps = cursor.fetchall()
            db.disconnectFromDb()
            num_of_pending = len(existing_apps)
            #list containing tuples. each tuple represents a pending application
            parameters_for_template = {"existing_apps":existing_apps,"num_of_pending":num_of_pending}
            template = jinja_environment.get_template('walker_app_interface.html')
            self.response.write(template.render(parameters_for_template))
        else:
        #walker can't view his existing walk applications before signing up
            self.redirect('/sign_up_walker')

    def post(self):
        user = users.get_current_user()
        email = user.email()
        db = db_handler.DbHandler()
        db.connectToDb()
        cursor = db.getCursor()
        sql_app = """SELECT Day_Requested, Shift_Requested, Submit_Date, Owner_Name, Owner_Phone, wa.Owner_email, Size, App_ID
                    FROM Walk_App AS wa 
                    JOIN Owner AS o ON o.Owner_Email=wa.Owner_Email
                    JOIN Dog AS d ON d.Dog_ID=wa.Dog_ID
                    WHERE wa.Walker_Email=%s AND Status="pending"
                    ORDER BY Submit_Date; """
        cursor.execute(sql_app,[email])
        existing_apps_not_send = cursor.fetchall()
        existing_apps = []
        for app in existing_apps_not_send:
            logging.info(app)
            logging.info(app[7])
            response = self.request.get(str(app[7]))
            if response: #an answer was given - approve/decline
                sql_update_response = """UPDATE Walk_App SET Status = %s, Response_Date=curdate()
                                         WHERE App_ID=%s"""
                cursor.execute(sql_update_response,[response,app[7]])
                db.commit()
            #when the if doesn't happen the walker didn't respond to the application
            else:
                existing_apps.append(app) #this is the updated list showing only the pending applications that were not answered
        num_of_pending = len(existing_apps)
        parameters_for_template = {"existing_apps":existing_apps,"num_of_pending":num_of_pending}
        db.disconnectFromDb()
        template = jinja_environment.get_template('walker_app_interface.html')
        self.response.write(template.render(parameters_for_template))
        
class Calendar( webapp2.RequestHandler):      
    def get(self):
        email_check = check(self)
        if int(email_check[0]) == 1:
        #user has already signed up, no need to sign up again, so we send him to requested page to view his walks.
            user = users.get_current_user()
            email = user.email()
            db = db_handler.DbHandler()
            db.connectToDb()
            cursor = db.getCursor()
            sql_calendar = """SELECT Day_Requested, Shift_Requested, Owner_Name, Owner_Phone, wa.Owner_email, Size, Dog_Name, App_ID
                              FROM Walk_App AS wa 
                              JOIN Owner AS o ON o.Owner_Email=wa.Owner_Email
                              JOIN Dog AS d ON d.Dog_ID=wa.Dog_ID
                              WHERE wa.Walker_Email=%s AND Status="approved"
                              ORDER BY FIELD(day_requested, 'sunday','monday','tuesday','wednesday','thursday','friday','saturday'),
                              FIELD(shift_requested,'morning','afternoon','evening' );"""
            cursor.execute(sql_calendar,[email])
            walks_list = cursor.fetchall() #every item is a tuple which represents an application that has a status approved
            days = ["sunday","monday","tuesday","wednesday","thursday","friday","saturday"]
            shifts = ["morning","afternoon","evening"]
            day_shift = []
            for day in days:
                for shift in shifts:
                    day_shift.append((day,shift))
            num_of_walks = len(walks_list)
            parameters_for_template = {"walks_list":walks_list,"day_shift":day_shift,"len":num_of_walks,"shifts":shifts,"days":days}
            db.disconnectFromDb()
            template = jinja_environment.get_template('calendar.html')
            self.response.write(template.render(parameters_for_template))    
        else:
        #walker can't view his calendar before signing up
            self.redirect('/sign_up_walker')










    


    