from flask import Flask, request, make_response, jsonify
from flask.helpers import make_response
from flask_mongoengine import MongoEngine
import datetime
import uuid
import os

from helper_functions import mask_this_email, validEmail, validPhoneNumber

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

'''
For safety purposes, the password of mongodb is stored in the ".env" file, with the parameter "MONGOPWD". 
The database_name in this case is "API", you can replace it with your own database name. The collections were manually created in the database.
DB_URI can be replaced with your own DB_URI.
Some helper functions have been defined in the "helper_functions.py" file.
'''

database_name = "API"
mongodb_password = os.getenv('MONGOPWD')
DB_URI = "mongodb+srv://sak1sham:{}@cluster0.azvu4.mongodb.net/{}?retryWrites=true&w=majority".format(mongodb_password, database_name)
app.config["MONGODB_HOST"] = DB_URI

db = MongoEngine()
db.init_app(app)

'''
    Now the MongoDB setup is completed. Now, let's define the schemas for the data. There are 3 schemas that we will use: 
    1. User (Personal details of the user)
    2. referrals (Transactional Details)
    3. income (Referral Goals specified by the admin)

    More details on this in the README.md file
'''

class user(db.Document):
    first_name = db.StringField(required=True, max_length=50)
    last_name = db.StringField(max_length=50)
    email = db.EmailField(unique=False, required=True)
    password = db.StringField(required=True, max_length=50)
    phone_number = db.StringField(required=True)
    referral_code = db.StringField(unique=True, required=True)
    has_withdrawn = db.BooleanField(default=False)
    successfull_referrals = db.IntField(default=0)
    
    def to_json(self):
        '''
            Overload the to_json() function and custom define our own function
        '''
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "password": self.password,
            "phone_number": self.phone_number,
            "referral_code": self.referral_code,
            "has_withdrawn": self.has_withdrawn,
            "successful_referrals": self.successfull_referrals
        }

class referrals(db.Document):
    referred_user = db.StringField(unique=True, required=True)
    referred_by = db.StringField(required=True)
    timestamp = db.DateTimeField(required=True)
    award = db.IntField(required=True)

    def to_json(self):
        '''
            Overload the to_json() function and custom define our own function
        '''
        return {
            "referred_user": self.referred_user,
            "referred_by": self.referred_by,
            "timestamp": self.timestamp,
            "award": self.award
        }

    def get_details(self):
        '''
            Returns masked email address and other relevant details when some other user (referred_by) asks for it
        '''
        email = mask_this_email(user.objects(referral_code=self.referred_user).first().email)
        return {
            "email": email,
            "timestamp": self.timestamp,
            "award": self.award
        }

class income(db.Document):
    referral_count = db.IntField(unique=True, required=True)
    award = db.IntField(required=True)
    
    def to_json(self):
        '''
            Overload the to_json() function and custom define our own function.
        '''
        return {
            "referral_count": self.referral_count,
            "award": self.income
        }
    
    def to_json_obj(self, obj):
        '''
            Return details of the milestone with additional parameter specifying whether user has achieved it or not.
            obj: specifies the user for whom the milestones are asked
        '''
        if(obj.successfull_referrals >= self.referral_count):
            return {
                "referral_count": self.referral_count,
                "award": self.award,
                "achieved": "Yes"
            }
        else:
            return {
                "referral_count": self.referral_count,
                "award": self.award,
                "achieved": "No"
            }

@app.route('/api/enroll', methods=['POST'])
def newUser():
    '''
        Creates a user with these details
            1. first name
            2. last name
            3. email
            4. password
            5. phone number
            6. referred_by (if any)
        If parameters(1-5) not valid, it returns code 404 specifying the error.
        parameter 6 is optional, but if persent it should be valid
        Adds the data to the user collection, and adds the referral transaction if any
    '''
    first_name = request.args.get('first_name', default="########")
    last_name = request.args.get('last_name', default="########")
    email = request.args.get('email', default="########")
    password = request.args.get('password', default="########")
    phone_number = request.args.get('phone_number', default="########")
    referred_by = request.args.get('referred_by', default="########")

    '''
        Check if parameters are valid, referral if present is valid, and email is not already present
    '''
    if(first_name == "########" or last_name == "########" or password == "########"):
        return make_response("Missing/Invalid Fields.", 404)
    elif(not validEmail(email)):
        return make_response("Missing/Invalid Email Address.", 404)
    elif(not validPhoneNumber(phone_number)):
        return make_response("Missing/Invalid Phone Number.", 404)

    for u in user.objects:
        if(email == u.email and u.has_withdrawn == False):
            return make_response("Email already Registered.", 404)
    
    validreferral = False
    if(referred_by == "########"):
        validreferral = True
    
    for u in user.objects:
        if(referred_by == u.referral_code and u.has_withdrawn == False):
            u.update(successfull_referrals = u.successfull_referrals+1)
            validreferral = True
            break
    
    if(not validreferral):
        return make_response("Invalid Referral", 404)
    
    '''
        Generate a new random referral ID for the new user. Double check if not already present.
    '''
    id = str(uuid.uuid4())
    while(True):
        id = str(uuid.uuid4())
        flag = False
        for u in user.objects:
            if(id == u.referral_code):
                flag = True
        if(not flag):
            break

    if(referred_by != "########"):
        '''
            If user was referred by someone, add transaction
        '''
        curr_count = user.objects(referral_code=referred_by).first().successfull_referrals
        mstone = income.objects(referral_count=curr_count)
        if(len(mstone) == 1):
            referrals_ = referrals(referred_user=id, referred_by=referred_by, timestamp=datetime.datetime.now(), award=mstone.first().award)
            referrals_.save()
        else:
            referrals_ = referrals(referred_user=id, referred_by=referred_by, timestamp=datetime.datetime.now(), award=0)
            referrals_.save()

    user_ = user(first_name=first_name, last_name=last_name, email=email, password=password, phone_number=phone_number, referral_code=id, has_withdrawn=False, successfull_referrals=0)
    user_.save()

    return make_response("Account Added Successfully.", 201)

@app.route('/api/referralCode', methods=['GET'])
def getReferralCode():
    '''
        Returns the referral code of the user with the following details
            1. email
        If email is not valid, it returns code 404 specifying the error.
    '''
    email = request.args.get('email', default="########")
    if(not validEmail(email)):
        return make_response("Invalid Email Address.", 404)

    for u in user.objects:
        if(email == u.email and u.has_withdrawn == False):
            return make_response(u.referral_code, 201)
    
    return make_response("Email Not Found.", 404)

@app.route('/api/withdraw', methods=['POST'])
def withdraw():
    '''
        Withdraws the user with the following details from the referral system
            1. email
        If email is not valid, it returns code 404 specifying the error.
    '''
    email = request.args.get('email', default="########")
    if(not validEmail(email)):
        return make_response("Invalid Email Address.", 404)

    for u in user.objects:
        if(email == u.email and u.has_withdrawn == False):
            u.update(has_withdrawn=True)
            return make_response("Account successfully Withdrawn.", 201)
    
    return make_response("Email Not Found.", 404)

@app.route('/api/milestones', methods=['GET'])
def milestones():
    '''
        Returns the milestones specified by the admin, meanwhile specifying which milestones have been achieved. user provides the following details
            1. email
        If email is not valid, it returns code 404 specifying the error.
    '''
    email = request.args.get('email', default="########")
    if(not validEmail(email)):
        return make_response("Invalid Email Address.", 404)
    
    for u in user.objects:
        if(email == u.email and u.has_withdrawn == False):
            ret = []
            for i in income.objects():
                ret.append(i.to_json_obj(u))
                
            return make_response(jsonify(ret), 201)

    return make_response("Email Not Found.", 404)

@app.route('/api/addMilestone', methods=['POST'])
def addMilestone():
    '''
        Adds a new milestone with the following details from the referral system
            1. count: Number of referrals
            2. award: money achieved by referring 'count' number of people
        If the values are not valid, it returns code 404 specifying the error.
        Return nothing.
    '''
    count = request.args.get('referral_count', default="########")
    award = request.args.get('award', default="########")
    
    if(not count.isdigit() or not award.isdigit()):
        return make_response("Invalid Milestone Entries.", 404)

    if(len(income.objects(referral_count=count)) > 0):
        return make_response("Milestone Already Present.", 404)
    
    income_ = income(referral_count=count, award=award)
    income_.save()
    return make_response("Milestone Added.", 201)

@app.route('/api/referralHistory', methods=['GET'])
def referralHistory():
    '''
        Returns the referralHistory of the user with the following details
            1. email
        If email is not valid, it returns code 404 specifying the error.
        Returns the masked email address of the person_referred, timestamp, and a value specifying whether the particular transaction led to completion of a milestone
    '''
    email = request.args.get('email', default="########")
    if(not validEmail(email)):
        return make_response("Invalid Email Address.", 404)

    for u in user.objects:
        if(email == u.email and u.has_withdrawn == False):
            my_code = u.referral_code
            ret = []
            for ref in referrals.objects(referred_by=my_code):
                ret.append(ref.get_details())
            return make_response(jsonify(ret), 201)
    
    return make_response("Email Not Found.", 404)

if __name__ == '__main__':
    app.run()
