from flask import Response
from flask import Flask, jsonify, request,redirect
from flask_restful import Resource, Api
from flask_cors import CORS
from datetime import datetime
import smtplib
from Database import Database
import os
import schedule
import time
import string
import random
from decouple import config
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from geopy.geocoders import Nominatim
import os
now = datetime.now().date()
# def print_date_time():
#     print(time.strftime("%A, %d. %B %Y %I:%M:%S %p"))


app=Flask(__name__)
CORS(app)
api=Api(app)

def verificationToken(token):
    try:
        object = jwt.decode(token, "secret", algorithms=["HS256"])
        print(object)

        return True
    except:
        return False
    

class Usermanagement(Resource):
    def __init__(self):
        self.db=Database()

    def post(self,pk=None):
        data = request.get_json()
        try:
            self.db.insert(f"INSERT INTO users(email,password) values('{data.get('email')}','{data.get('password')}')")
            return {"status":"success"}
        except Exception as e:
            print(e)
            return {"status":"Failed Input"}

    def get(self,pk=None):
        if pk==None:
            res = self.db.query('SELECT * FROM users')
        else:
            res = self.db.query(f'SELECT * FROM users where id={pk}')
        return {"data":res}

    def delete(self,pk):
        try:
            self.db.insert(f'DELETE FROM users where id={pk}')
            return {"data":"success"}
        except:
            return {"status":"Failed"}

    def get(self,pk=None):
        if pk==None:
            res = self.db.query('SELECT * FROM users')
        else:
            res = self.db.query(f'SELECT * FROM users where id={pk}')
        return {"data":res}

    def delete(self,pk):
        try:
            self.db.insert(f'DELETE FROM users where id={pk}')
            return {"data":"success"}
        except:
            return {"status":"Failed"}
    
    def put(self,pk):
        data = request.get_json()
        try:
            self.db.insert(f"UPDATE users set email='{data.get('email')}',password='{data.get('password')}' where id={pk}")
            return {"status":"Success"}
        except Exception as e:
            return {"status":"Failed"}

class Login(Resource):
    def __init__(self):
        self.db=Database()

    def post(self,pk=None):
        data = request.get_json()
        print(data)
        try:
            res = self.db.query(f"SELECT * FROM users where email='{data.get('email')}' and password='{data.get('password')}'")
            if(res==[]):
                print(res)
                return {"status":400}
            else:
                print(res[0][0])
                return {"id":res[0][0],"email":res[0][1],"email":res[0][1],"password":res[0][2],"status":201}
            
        except Exception as e:
            print(e)
            return {"status":"Failed Input"}



class Register(Resource):
    def __init__(self):
        self.db=Database()

    def post(self,pk=None):
        data = request.get_json()
        print(data)
        data_fetch = self.db.query(f"select * from users where email='{data.get('email')}'")
        
        if(len(data_fetch)>0):
            return {"status":"Failed Input"}
        try:
            # id = self.db.query("select max(id)+1 from users")
            res = self.db.insert(f"INSERT INTO users values(default,'{data.get('email')}','{data.get('password')}')")
            # id = self.db.query("select max(id) from users")
            return Response({"status":"Success"},status=201)
            
        except Exception as e:
            print(e)
            return {"status":"Failed Input"}


class Logs(Resource):
    def __init__(self):
        self.db=Database()
    
    def get(self):
        data_fetch = []
        listitems = []
        # try:
        data_fetch = self.db.query(f"SELECT * from logs")
        print(data_fetch)
        for x in data_fetch:
            if(x[4]):
                listitems.append({"id":x[0],"location":x[1],"quantity":x[2],"disease":x[3],"date":str(x[4])})
        # except Exception as e:
        #     print(e)
        # for x in data_fetch:
        #     print(x)
        return listitems

    def post(self,user_id=None):
        res = request.get_json()
        id = self.db.query(f"SELECT * FROM logs where disease='{res.get('disease')}'")
        # if(len(id)==0):
        data_fetch = self.db.insert(f"INSERT INTO logs values(default,'{res.get('location')}',1,'{res.get('disease')}','{now}')")
        # else:
        #     self.db.insert(f"UPDATE logs set quantity=quantity+1 where disease='{res.get('disease')}'")
        return



class LongLat(Resource):
    def __init__(self):
        self.db=Database()

    def post(self,user_id=None):
        res = request.get_json()
        aps = Nominatim(user_agent="tutorial")
        """This function returns an address as raw from a location
        will repeat until success"""
        # build coordinates string to pass to reverse() functio
        coordinates = f"{res.get('latitude')}, {res.get('longitude')}"
        location = aps.reverse(coordinates, language='en').raw
        print(location.get('address'))
        return f"{location.get('address').get('city')}, {location.get('address').get('state')}"


class Recipe(Resource):
    def __init__(self):
        self.db=Database()

    def get(self,menu_id=None):
        data_fetch = self.db.query(f"SELECT * FROM recipe where menu_id={menu_id}")
        return data_fetch

    def post(self,user_id=None):
        res = request.get_json()
        data_fetch = self.db.insert(f"INSERT INTO recipe values(default,'{res.get('name')}',{res.get('user_id')},1)")
        return

        
    


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class ResetPassword(Resource):
    def __init__(self):
        self.db=Database()
        
    def post(self):
        res = request.get_json()
        pw = id_generator()
        print(res)
        isValid = self.db.query(f"select * from users where email='{res.get('email')}' ")
        if(len(isValid) > 0):
            self.db.insert(f"UPDATE users set password='{pw}' where email='{res.get('email')}' ")
            msg = MIMEMultipart()
            msg.add_header('Content-Type', 'text/html')
            msg['To'] = str(res.get('email'))
            msg['Subject'] = "Reset password from CALAHEALTH app"
            part1=MIMEText("""\
                <html>
                    <body>
                        Here's your new password : """+pw+"""
                    </body>
                </html>
                
                """,'html')

            msg.attach(part1)
            server = smtplib.SMTP('smtp.gmail.com: 587')
            server.starttls()
            server.login('usagi.reboot@gmail.com', "12899bbc")
            # send the message via the server.
            server.sendmail('usagi.reboot@gmail.com', msg['To'], msg.as_string())
            server.quit()
            print("successfully sent email to %s:" % (msg['To']))
            return {"status":"success"}
        else:
            print("invalid")
            return {"status":"invalid"}

api.add_resource(Register,'/api/v1/register')   
api.add_resource(Usermanagement,'/api/v1/users/<int:pk>')
api.add_resource(Login,'/api/v1/login')
api.add_resource(LongLat,'/api/v1/longlat')
api.add_resource(Logs,'/api/v1/logs')
api.add_resource(ResetPassword,'/api/v1/reset_password')
# api.add_resource(UploadTest,'/api/v1/uploadtest')
if __name__ == "__main__":
    app.run(debug=True,host='localhost',port="5001")
