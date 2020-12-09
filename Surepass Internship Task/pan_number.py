from flask import Flask, make_response, request,jsonify
from flask_mongoengine import MongoEngine
from flask_restx import Resource, Api
from random import randrange
from credential import db_password
import jwt
from functools import wraps
import requests

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'theskyisblue' #secret key for token generation

db = MongoEngine()
db.init_app(app)
db.disconnect()  # disconnects if database is already connected to some other server

#connecting to the Mongo database
database_name = "PANdata"
password = db_password
DB_URI = "mongodb+srv://anjum_r:{}@pythoncluster.o2mjq.mongodb.net/{}?retryWrites=true&w=majority".format(password,database_name)
db.connect(db=database_name, username='anjum_r', password=password, host=DB_URI)
app.config["MONGODB_HOST"] = DB_URI

#feeding data into the database
class PAN(db.Document):
	    pan = db.StringField()
	    name = db.StringField()
	    dob = db.DateField()
	    father_name = db.StringField()
	    client_id = db.StringField()

	    def to_json(self):
	        """
	        to return the document in JSON format
	        """ 
	        return{
	            "pan": self.pan,
	            "name": self.name,
	            "dob": self.dob,
	            "father_name": self.father_name,
	            "client_id": self.client_id}
	      
p_a_n = PAN(
		pan = "ANRPM2537K",
		name = "Dinesh Kumar",
		dob = "1990-10-25",
		father_name = "Hari Kumar",
		client_id = "4feb601e-2316-4dda-8d91-28c89cdb2335"
		)

p_a_n.save() #saving the above data in the collection
#print(p_a_n.name)

#Decorator function to check if the token entered is valid or not, for each request
def token_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		token = request.args.get('token')

		if not token:
			return jsonify({'message': 'Token is missing!'}), 403
		try:
			data = jwt.decode(token, app.config['SECRET_KEY'])
		except:
			return jsonify({'message': 'Token is invalid!'}), 403
		return f(*args, **kwargs)
	return decorated

# Bearer Token generation after successful login, to be used in further requests (First Endpoint)
@app.route('/user_login')
def user_login():
	auth = request.authorization
	#if username matches with the PAN number, then the token will be generated successfully
	if auth and auth.username == p_a_n.pan and auth.password == 'password':   
		token = jwt.encode({'user': auth.username}, app.config['SECRET_KEY'])
		
		return jsonify({'token' : token.decode('UTF-8')})

	return make_response('Could not verify!', 401, {'WWW-Authenticate' : 'Basic realm="Login Required"'})


@app.route('/validity')      #Second Endpoint
@token_required
def validity():
	return {'client_id': p_a_n.client_id}

@app.route('/obtain_data')  #Third Endpoint
@token_required
def obtain_data():
	return make_response(jsonify({'pan':p_a_n.pan},{'name':p_a_n.name},{'dob':p_a_n.dob},{'father_name':p_a_n.father_name})),201

class BackendError(Exception):
    pass


def get_pan_data(pan_number):
	pan_number=str(pan_number)

	num = randrange(10)
	print(num)
	try:
		if num in (8,9):
	 		raise BackendError
	 		
	except BackendError:
		print("Website server unavailable!") 

	if num==8 or num==9:
		print('')
	else:
		print({
	    	'pan': pan_number,
	        'name': 'Dinesh Kumar',
	        'dob': '25-10-1990',
	        'father_name': 'Hari Kumar'
	         })
get_pan_data("ANRPM2537K")

if __name__ == '__main__':
    app.run(debug=True)