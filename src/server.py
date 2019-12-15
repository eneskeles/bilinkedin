from flask import Flask
from flask import request
from flask_cors import CORS
import json
import itertools
from db_interface import *
from datetime import date

app = Flask(__name__)
CORS(app)

def string_to_date(isostr):
    splitted_str = isostr.split('-')
    return date(int(splitted_str[0]), int(splitted_str[1]), int(splitted_str[2]))

def string_to_datetime(isostr):
    date = isostr.split(' ')[0]
    splitted_date = date.split('-')

    time = isostr.split(' ')[1]
    splitted_time = time.split(':')
    return datetime.datetime(int(splitted_date[0]), int(splitted_date[1]), int(splitted_date[2]),
                             int(splitted_time[0]), int(splitted_time[1]), int(splitted_time[2]))

def check_json_fields(req_json, json_fields):
    if not req_json:
      return False
    for json_field in json_fields:
        if not req_json.get(json_field):
            return False
    return True

def check_args_fields(args, args_fields):
    if not args:
        return False
    for args_field in args_fields:
        if not args.get(args_field):
            return False
    return True

@app.route('/professional_login/', methods = ['POST'])
def professional_login(): 
    json_fields = ['email', 'password']
    req_json = request.get_json()
    if check_json_fields(req_json, json_fields):
        user_id = validate_professional(req_json['email'], req_json['password'])
        if  user_id != -1:
            token = add_active_user(user_id)
            professional, avg_rating = get_professional_profile(user_id)
            return json.dumps({
                                'token': token,
                                'username': professional[2]
                              }, indent=4), 200
        else:
            return json.dumps({'error': 'wrong credentials.'}), 401
    else:
        return json.dumps({'error': 'some fields are missing.'}), 400


@app.route('/customer_login/', methods = ['POST'])
def customer_login(): 
    json_fields = ['email', 'password']
    req_json = request.get_json()
    if check_json_fields(req_json, json_fields):
        user_id = validate_customer(req_json['email'], req_json['password'])
        if  user_id != -1:
            token = add_active_user(user_id)
            customer, avg_rating = get_customer_profile(user_id)
            return json.dumps({
                                'token': token,
                                'username': customer[2]
                              }, indent=4), 200
        else:
            return json.dumps({'error': 'wrong credentials.'}), 401
    else:
        return json.dumps({'error': 'some fields are missing.'}), 400


@app.route('/professional_register/', methods = ['POST']) 
def professional_register():
    json_fields = ['username', 'password', 'firstname', 'lastname', 'email', 'fields']
    req_json = request.get_json()
    if check_json_fields(req_json, json_fields):
        if check_professional(req_json['email']) == -1:
            add_professional(req_json['username'], req_json['password'],
                             req_json['firstname'], req_json['lastname'],
                             req_json['email'], req_json['fields'])
            return json.dumps({'success': 'the professional is added.'}), 200
        else:
            return json.dumps({'error' : 'username or email already in use.'}), 401
    else:
        return json.dumps({'error': 'some fields are missing.'}), 400

@app.route('/customer_register/', methods = ['POST'])
def customer_register():
    json_fields = ['username', 'password', 'firstname', 'lastname', 'email']
    req_json = request.get_json()
    if check_json_fields(req_json, json_fields):
        if check_customer(req_json.get('email')) == -1:
            add_customer(req_json['username'], req_json['password'],
                             req_json['firstname'], req_json['lastname'],
                             req_json['email'])
            return json.dumps({'success': 'the customer is added.'}), 200
        else:
            return json.dumps({'error' : 'username or email already in use.'}), 401
    else:
        return json.dumps({'error': 'some fields are missing.'}), 400

# to view a professional's profile send a GET request with token and user_id
# to edit self profile send a post request with token, user_id, username, email, fields
@app.route('/professional_profile/', methods = ['GET', 'POST'])
def professional_profile():
    if request.method == 'GET':
        args_fields = ['token', 'username']
        if check_args_fields(request.args, args_fields):
            if get_user_id_by_token(request.args['token']) != -1:
                user_id = get_pro_id_by_username(request.args['username'])
                professional, avg_rating = get_professional_profile(user_id)
                if professional == -1:
                    return json.dumps({'error': 'the user is not a professional.'})
                else:
                    fields = get_professional_fields(user_id)
                    fields_summed = []
                    for field in fields:
                        fields_summed.append(field[0])
                    return json.dumps({
                        "username": professional[2],
                        "email": professional[4],
                        "firstname": professional[0],
                        "lastname" : professional[1],
                        "balance" : professional[3],
                        "avg_rating": avg_rating,
                        "fields" : fields_summed
                    }, indent=4), 200
            else:
                return json.dumps({'error' : 'you are not logged in.'}), 401
        else:
            return json.dumps({'error': 'some fields are missing.'}), 400

    if request.method == 'POST':
        json_fields = ['token', 'username', 'email', 'fields']
        req_json = request.get_json()
        if check_json_fields(req_json, json_fields):
            user_id = get_user_id_by_token(req_json['token'])
            if user_id != -1:
                update_professional(user_id, req_json['email'], req_json['username'], req_json['fields'])
                return json.dumps({'success' : 'the professional is updated.'}), 200
            else:
                return json.dumps({'error' : 'either you are not logged in or you are not authorized to do this.'}), 401
        else:
            return json.dumps({'error': 'some fields are missing.'}), 400

# to get a customer's profile send a GET request with token and user_id
# to edit self profile send a post request with token, user_id, username, email
@app.route('/customer_profile/', methods = ['GET', 'POST'])
def customer_profile():
    if request.method == 'GET':
        args_fields = ['token', 'username']
        if check_args_fields(request.args, args_fields):
            if get_user_id_by_token(request.args['token']) != -1:
                user_id = get_cus_id_by_username(request.args['username'])
                customer, avg_rating = get_customer_profile(user_id)
                if customer == -1:
                    return json.dumps({'error': 'the user is not a customer.'}), 401
                else:
                    return json.dumps({
                        "username": customer[2],
                        "email": customer[4],
                        "firstname": customer[0],
                        "lastname": customer[1],
                        "balance": customer[3],
                        "avg_rating" : avg_rating
                    }, indent=4), 200
            else:
                return json.dumps({'error': 'you are not logged in.'}), 401
        else:
            return json.dumps({'error': 'some fields are missing.'}), 400

    if request.method == 'POST':
        json_fields = ['token', 'username', 'email']
        req_json = request.get_json()
        if check_json_fields(req_json, json_fields):
            user_id = get_user_id_by_token(req_json['token'])
            if user_id != -1:
                update_customer(user_id, req_json['email'], req_json['username'])
                return json.dumps({'success': 'the customer is updated.'}), 200
            else:
                return json.dumps({'error': 'either you are not logged in or you are not authorized to do this.'}), 401
        else:
            return json.dumps({'error': 'some fields are missing.'}), 400

# amount check can be written in SQL
@app.route('/add_deposit/', methods = ['POST'])
def add_deposit():
    json_fields = ['token', 'amount', 'role']
    req_json = request.get_json()
    if check_json_fields(req_json, json_fields):
        user_id = get_user_id_by_token(req_json['token'])
        amount = int(req_json['amount'])
        if user_id == -1:
            return json.dumps({'error': 'you are not logged in.'}), 401
        if amount > 0:
            add_to_balance(user_id, amount, req_json['role'])
            return json.dumps({'success': 'the balance is updated.'}), 200
        else:
            return json.dumps({'error': 'the amount is negative.'}), 401
    else:
        return json.dumps({'error': 'some fields are missing.'}), 400

# a customer's reviews given the user_id
@app.route('/customer_reviews/', methods = ['GET'])
def customer_reviews():
    args_fields = ['token', 'username']
    if check_args_fields(request.args, args_fields):
        user_id = get_cus_id_by_username(request.args['username'])
        if get_user_id_by_token(request.args['token']) != -1:
            reviews, review_ids = get_customer_reviews(user_id)
            result = []
            for review, review_id in zip(reviews, review_ids):
                result.append({
                    'review_id' : review_id[0],
                    'review_text': review[0],
                    'rating': review[1],
                    'username': review_id[1]
                })
            return json.dumps({'reviews' : result}), 200
        else:
            return json.dumps({'error': 'you are not logged in.'}), 401
    else:
        return json.dumps({'error': 'some fields are missing.'}), 400

# a professional's reviews given the user_id
@app.route('/professional_reviews/', methods = ['GET'])
def professional_reviews():
    args_fields = ['token', 'username']
    if check_args_fields(request.args, args_fields):
        user_id = get_pro_id_by_username(request.args['username'])
        if get_user_id_by_token(request.args['token']) != -1:
            reviews, review_ids = get_professional_reviews(user_id)
            result = []
            for review, review_id in zip(reviews, review_ids):
                result.append({
                    'review_id' : review_id[0],
                    'review_text': review[0],
                    'rating': review[1],
                    'username': review_id[1]
                })
            return json.dumps({'reviews' : result}), 200
        else:
            return json.dumps({'error': 'you are not logged in.'}), 401
    else:
        return json.dumps({'error': 'some fields are missing.'}), 400

# to customers to publish announcements
@app.route('/publish_announcement/', methods = ['POST'])
def publish_announcement():
    json_fields = ['token', 'title', 'description', 'start_date', 'end_date', 
        'max_price', 'location', 'field']
    req_json = request.get_json()
    if check_json_fields(req_json, json_fields):
        start_date = string_to_date(req_json['start_date'])
        end_date = string_to_date(req_json['end_date'])
        user_id = get_user_id_by_token(req_json['token'])
        if user_id != -1:
            if int(req_json['max_price']) >= 0:
                add_announcement(user_id, req_json['title'], req_json['description'], start_date,
                                 end_date, req_json['max_price'], req_json['location'], req_json['field'])
                return json.dumps({'success': 'the announcement is published.'}), 200
            else:
                return json.dumps({'error' : 'maximum price cannot be negative'}), 401
        else:
            return json.dumps({'error': 'you are not logged in.'}), 401
    else:
        return json.dumps({'error': 'some fields are missing.'}), 400

@app.route('/get_announcement/', methods = ['GET'])
def get_announcement():
    args_fields = ['token', 'announcement_id']
    print(request.args['announcement_id'])
    if check_args_fields(request.args, args_fields):
        if get_user_id_by_token(request.args['token']) != -1:
            announcement, announcer, avg_rating = get_announcement_by_id(request.args['announcement_id'])
            return json.dumps({
                                'title' : announcement[2],
                                'description' : announcement[3],
                                'start_date' : announcement[4],
                                'end_date' : announcement[5],
                                'max_price' : announcement[6],
                                'location' : announcement[7],
                                'field' : announcement[8],
                                'username' : announcer[1],
                                'avg_rating' : avg_rating
                              }, indent = 4)
        else:
            return json.dumps({'error': 'you are not logged in.'}), 401
    else:
        return json.dumps({'error': 'some fields are missing.'}), 400

@app.route('/customer_announcements/', methods = ['GET'])
def customer_announcements():
    args_fields = ['token']
    if check_args_fields(request.args, args_fields):
        user_id = get_user_id_by_token(request.args['token'])
        if user_id != -1:
            announcements = get_customer_announcements(user_id)
            result = []
            for announcement in announcements:
                result.append({
                                'announcement_id' : announcement[0],
                                'title': announcement[2],
                                'description': announcement[3],
                                'start_date': announcement[4],
                                'end_date': announcement[5],
                                'max_price': announcement[6],
                                'location': announcement[7],
                                'field': announcement[8]
                              })
            return json.dumps({'announcements' : result})
    else:
        return json.dumps({'error': 'some fields are missing.'}), 400

@app.route('/available_jobs/', methods = ['GET'])
def available_jobs():
    args_fields = ['token']
    if check_args_fields(request.args, args_fields):
        user_id = get_user_id_by_token(request.args['token'])
        if user_id != -1:
            jobs, avg_ratings = get_available_jobs(user_id)
            result = []
            for job, avg_rating in zip(jobs, avg_ratings):
                result.append({
                                'announcement_id' :job[0],
                                'title' : job[1],
                                'description' : job[2],
                                'start_date' : job[3],
                                'end_date' : job[4],
                                'max_price' : job[5],
                                'location' : job[6],
                                'field' : job[7],
                                'username' : job[8],
                                'avg_rating' : avg_rating
                              })

            return json.dumps({'jobs' : result}, indent=4), 200
        else :
            return json.dumps({'error': 'you are not logged in.'}), 401
    else:
        return json.dumps({'error': 'some fields are missing.'}), 400


@app.route('/make_offer/', methods = ['POST'])
def make_offer():
    json_fields = ['token', 'announcement_id', 'description', 'start_date', 'end_date', 'price']
    req_json = request.get_json()
    if check_json_fields(req_json, json_fields):
        user_id = get_user_id_by_token(req_json['token'])
        if user_id != -1:
            start_date = string_to_date(req_json['start_date'])
            end_date = string_to_date(req_json['end_date'])
            add_offer(user_id, request.json['announcement_id'], request.json['description'], start_date,
                      end_date, request.json['price'])
            return json.dumps({'success': 'the offer is added.'}), 200
        else:
            return json.dumps({'error': 'you are not logged in.'}), 401
    else:
        return json.dumps({'error': 'some fields are missing.'}), 400

@app.route('/dismiss_offer/', methods= ['POST'])
def dismiss_offer():
    json_fields = ['token', 'offer_id']
    req_json = request.get_json()
    if check_json_fields(req_json, json_fields):
        if get_user_id_by_token(req_json['token']) != -1:
            delete_offer(req_json['offer_id'])
            return json.dumps({'success': 'the offer is dismissed.'}), 200
        else:
            return json.dumps({'error': 'you are not logged in.'}), 401
    else:
        return json.dumps({'error': 'some fields are missing.'}), 400


# offers done to this customer's announcements
@app.route('/customer_view_offers/', methods = ['GET'])
def customer_view_offers():
    args_fields = ['token']
    if check_args_fields(request.args, args_fields):
        user_id = get_user_id_by_token(request.args['token'])
        if user_id != -1:
            offers, avg_ratings = get_offers_customer(user_id)
            result = []
            for offer, avg_rating in zip(offers, avg_ratings):
                announcement_id = offer[7]
                announcement, announcer, avg_rating = get_announcement_by_id(announcement_id)
                result.append({
                                "offer_id": offer[0],
                                "description": offer[2],
                                "start_date": offer[3],
                                "end_date": offer[4],
                                "cost": offer[5],
                                "username": offer[6],
                                "avg_rating": avg_rating,
                                'announcement_title': announcement[2]
                              })
            return json.dumps({'offers' : result}, indent = 4), 200
        else:
            return json.dumps({'error': 'you are not logged in.'}), 401
    else:
        return json.dumps({'error': 'some fields are missing.'}), 400

# offers done by this professional
@app.route('/professional_view_offers/', methods = ['GET'])
def professional_view_offers():
    args_fields = ['token']
    if check_args_fields(request.args, args_fields):
        user_id = get_user_id_by_token(request.args['token'])
        if user_id != -1:
            offers, avg_ratings = get_offers_professional(user_id)
            result = []
            for offer, avg_rating in zip(offers, avg_ratings):
                announcement_id = offer[7]
                announcement, announcer, avg_rating = get_announcement_by_id(announcement_id)
                result.append({
                                "offer_id": offer[0],
                                "description": offer[2],
                                "start_date": offer[3],
                                "end_date": offer[4],
                                "cost": offer[5],
                                "username": offer[6],
                                "avg_rating": avg_rating,
                                'announcement_title' : announcement[2]
                              })
            return json.dumps({'offers' : result}, indent = 4), 200
        else:
            return json.dumps({'error': 'you are not logged in.'}), 401
    else:
        return json.dumps({'error': 'some fields are missing.'}), 400

@app.route('/offer_chat/', methods = ['GET', 'POST'])
def offer_chat():
    if request.method == 'GET':
        args_fields = ['token', 'offer_id']
        if check_args_fields(request.args, args_fields):
            user_id = get_user_id_by_token(request.args['token'])
            if user_id != -1:
                messages = get_offer_chat(request.args['offer_id'])
                result = []
                for message in messages:
                    result.append({
                                    'message_id' : message[0],
                                    'username' : get_username_by_id(message[2]),
                                    'message_text' : message[3],
                                    'date_and_time' : message[4]
                                  })
                return json.dumps({'offer_chat': result}), 200
            else:
                return json.dumps({'error': 'you are not logged in.'}), 401
        else:
            return json.dumps({'error': 'some fields are missing.'}), 400

    if request.method == 'POST':
        json_fields = ['token', 'offer_id', 'message_text', 'date_and_time']
        req_json = request.get_json()
        if check_json_fields(req_json, json_fields):
            user_id = get_user_id_by_token(req_json['token'])
            if user_id != -1:
                date_and_time = string_to_datetime(req_json['date_and_time'])
                add_to_offer_chat(user_id, req_json['offer_id'], req_json['message_text'], date_and_time)
                return json.dumps({'success': 'the message is added.'}), 200
            else:
                return json.dumps({'error': 'you are not logged in.'}), 401
        else:
            return json.dumps({'error': 'some fields are missing.'}), 400

# THAT COMMISSION WILL BE DELETED, CORRESPONDING OFFERS WILL BE DELETED
@app.route('/open_commission/', methods = ['POST'])
def open_commission():
    json_fields = ['token', 'offer_id']
    req_json = request.get_json()
    if check_json_fields(req_json, json_fields):
        user_id = get_user_id_by_token(req_json['token'])
        if user_id != -1:
            add_commission(user_id, req_json['offer_id'])
            return json.dumps({'success' : 'the commission is added.'}), 200
        else:
            return json.dumps({'error': 'you are not logged in.'}), 401

    else:
        return json.dumps({'error': 'some fields are missing.'}), 400


@app.route('/professional_commissions/', methods = ['GET'])
def professional_commissions():
    args_fields = ['token']
    if check_args_fields(request.args, args_fields):
        user_id = get_user_id_by_token(request.args['token'])
        if user_id != -1:
            commissions, announcers, avg_ratings = get_professional_commissions(user_id)
            result = []
            for index, commission in enumerate(commissions):
                announcer = announcers[index]
                avg_rating = avg_ratings[index]
                review_id = get_cus_review_id(commission[0])
                result.append({
                                "commission_id": commission[0],
                                "title": commission[1],
                                "status": commission[2],
                                "start_date" : commission[3],
                                "end_date": commission[4],
                                "cost" : commission[5],
                                "location" : commission[6],
                                "offer_text" : commission[7],
                                "username" : announcer[1],
                                "avg_rating" : avg_rating,
								"review_id" : review_id
                              })
            return json.dumps({'commissions': result}, indent=4)
        else:
            return json.dumps({'error': 'you are not logged in.'}), 401

    else:
        return json.dumps({'error': 'some fields are missing.'}), 400

@app.route('/customer_commissions/', methods = ['GET'])
def customer_commissions():
    args_fields = ['token']
    if check_args_fields(request.args, args_fields):
        user_id = get_user_id_by_token(request.args['token'])
        if user_id != -1:
            commissions, announcers, avg_ratings = get_customer_commissions(user_id)
            result = []
            for index, commission in enumerate(commissions):
                announcer = announcers[index]
                avg_rating = avg_ratings[index]
                review_id = get_pro_review_id(commission[0])
                result.append({
                                "commission_id": commission[0],
                                "title": commission[1],
                                "status": commission[2],
                                "start_date" : commission[3],
                                "end_date": commission[4],
                                "cost" : commission[5],
                                "location" : commission[6],
                                "offer_text" : commission[7],
                                "username" : announcer[1],
                                "avg_rating" : avg_rating,
								"review_id" : review_id
                              })
            return json.dumps({'commissions': result}, indent=4), 200
        else:
            return json.dumps({'error': 'you are not logged in.'}), 401

    else:
        return json.dumps({'error': 'some fields are missing.'}), 400

@app.route('/commission_chat/', methods = ['GET', 'POST'])
def commission_chat():
    if request.method == 'GET':
        args_fields = ['token', 'commission_id']
        if check_args_fields(request.args, args_fields):
            user_id = get_user_id_by_token(request.args['token'])
            if user_id != -1:
                messages = get_commission_chat(request.args['commission_id'])
                result = []
                for message in messages:
                    result.append({
                                    'message_id' : message[0],
                                    'username' : get_username_by_id(message[2]),
                                    'message_text' : message[3],
                                    'date_and_time' : message[4]
                                  })
                return json.dumps({'commission_chat': result}), 200
            else:
                return json.dumps({'error': 'you are not logged in.'}), 401
        else:
            return json.dumps({'error': 'some fields are missing.'}), 400

    if request.method == 'POST':
        json_fields = ['token', 'commission_id', 'message_text', 'date_and_time']
        req_json = request.get_json()
        if check_json_fields(req_json, json_fields):
            user_id = get_user_id_by_token(req_json['token'])
            if user_id != -1:
                date_and_time = string_to_datetime(req_json['date_and_time'])
                add_to_commission_chat(user_id, req_json['commission_id'], req_json['message_text'], date_and_time)
                return json.dumps({'success': 'the message is added.'}), 200
            else:
                return json.dumps({'error': 'you are not logged in.'}), 401
        else:
            return json.dumps({'error': 'some fields are missing.'}), 400

a = '''
@app.route('/customer_leave_review/', methods = ['POST'])
def customer_leave_review():
    json_fields = ['token', 'commission_id', 'review_text', 'rating'] 
    if check_json_fields(request, json_fields):
        # TODO 
        return dummy_json 

    else:
        return json.dumps({'error': 'some fields are missing.'}), 400

@app.route('/professional_leave_review/', methods = ['POST'])# TODO
def professional_leave_review():
    json_fields = ['token', 'commission_id', 'review_text', 'rating'] 
    if check_json_fields(request, json_fields):
        # TODO 
        return dummy_json 

    else:
        return json.dumps({'error': 'some fields are missing.'}), 400
'''

@app.route('/logout/', methods = ['POST'])
def logout():
    json_fields = ['token']
    req_json = request.get_json()
    if check_json_fields(req_json, json_fields) != -1:
        user_id = get_user_id_by_token(req_json['token'])
        if user_id != -1:
            remove_active_user_byid(user_id)
            return json.dumps({'success' : 'succesfully logged out.'})
        else:
            return json.dumps({'error' : 'no such token.'}), 200
    else:
        return json.dumps({'error': 'some fields are missing.'}),400


@app.route('/complete_commission_professional/', methods = ['POST'])
def commission_pro_complete():
	json_fields = ['token', 'commission_id'] #TODO no check is done to see if commission belongs to user, maybe check it?
	req_json = request.get_json()
	if check_json_fields(req_json, json_fields):
		user_id = get_user_id_by_token(req_json['token'])
		commission_id = req_json['commission_id']
		if user_id != -1:
			commission_mark_complete_pro(req_json['commission_id'])
			return json.dumps({'success' : 'the commission is marked as complete.'}), 200
		else:
			return json.dumps({'error': 'you are not logged in.'}), 401
	else:
		return json.dumps({'error': 'some fields are missing.'}), 400
		
@app.route('/complete_commission_customer/', methods = ['POST'])
def commission_cus_complete():
	json_fields = ['token', 'commission_id'] #TODO no check is done to see if commission belongs to user, maybe check it?
	req_json = request.get_json()
	if check_json_fields(req_json, json_fields):
		user_id = get_user_id_by_token(req_json['token'])
		commission_id = req_json['commission_id']
		if user_id != -1:
			commission_mark_complete_cus(req_json['commission_id'])
			return json.dumps({'success' : 'the commission is marked as complete.'}), 200
		else:
			return json.dumps({'error': 'you are not logged in.'}), 401
	else:
		return json.dumps({'error': 'some fields are missing.'}), 400


if __name__ == '__main__':
    app.run(debug=True)    

	
	
	
@app.route('/send_review_professional/', methods = ['POST'])
def send_review_professional():
	json_fields = ['token', 'commission_id','rating','review_text'] #TODO no check is done to see if commission belongs to user, maybe check it?
	req_json = request.get_json()
	if check_json_fields(req_json, json_fields):
		user_id = get_user_id_by_token(req_json['token'])
		commission_id = req_json['commission_id']
		rating = req_json['rating']
		review_text = req_json['review_text']
		if user_id != -1:
			add_review_to_customer(commission_id,rating,review_text)
			return json.dumps({'success' : 'review made'}), 200
		else:
			return json.dumps({'error': 'you are not logged in.'}), 401
	else:
		return json.dumps({'error': 'some fields are missing.'}), 400
		
@app.route('/send_review_customer/', methods = ['POST'])
def send_review_customer():
	json_fields = ['token', 'commission_id','rating','review_text'] #TODO no check is done to see if commission belongs to user, maybe check it?
	req_json = request.get_json()
	if check_json_fields(req_json, json_fields):
		user_id = get_user_id_by_token(req_json['token'])
		commission_id = req_json['commission_id']
		rating = req_json['rating']
		review_text = req_json['review_text']
		if user_id != -1:
			add_review_to_professional(commission_id,rating,review_text)
			return json.dumps({'success' : 'review made'}), 200
		else:
			return json.dumps({'error': 'you are not logged in.'}), 401
	else:
		return json.dumps({'error': 'some fields are missing.'}), 400