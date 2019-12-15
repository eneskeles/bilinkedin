import sqlite3
import secrets
import json
import datetime
conn = sqlite3.connect('bilinkedin.db')
cur = conn.cursor()


# -> validate_professional(email, password) - returns user_id, -1 if not correct
def validate_professional(email, password):
    conn = sqlite3.connect('bilinkedin.db')
    cur = conn.cursor()
    ret = cur.execute('''
		SELECT user_id
		FROM Professional
		WHERE Professional.email == ? AND Professional.password == ?;
	''', (email, password))
    ret = ret.fetchone()
    cur.close()
    return ret[0] if ret != None else -1


def validate_customer(email, password):
    conn = sqlite3.connect('bilinkedin.db')
    cur = conn.cursor()
    ret = cur.execute('''
		SELECT user_id
		FROM Customer
		WHERE Customer.email == ? AND Customer.password == ?;
	''', (email, password))
    ret = ret.fetchone()
    cur.close()
    return ret[0] if ret != None else -1


# -> check_professional(email) - returns user_id if email is in use, -1 else
def check_professional(email):  ##oneri: bunu get_professional_id olarak refactorleyelim daha mantikli olur gibi idk
    conn = sqlite3.connect('bilinkedin.db')
    cur = conn.cursor()
    ret = cur.execute('''
		SELECT user_id
		FROM Professional
		WHERE Professional.email == ?;
	''', (email,))
    ret = ret.fetchone()
    cur.close()
    return ret[0] if ret != None else -1


def check_customer(email):  ##oneri: bunu get_professional_id olarak refactorleyelim daha mantikli olur gibi idk
    conn = sqlite3.connect('bilinkedin.db')
    cur = conn.cursor()
    ret = cur.execute('''
		SELECT user_id
		FROM Customer
		WHERE Customer.email == ?;
	''', (email,))
    ret = ret.fetchone()
    cur.close()
    return ret[0] if ret != None else -1

def get_username_by_id(user_id):
    conn = sqlite3.connect('bilinkedin.db')
    cur = conn.cursor()
    result = cur.execute('''
        SELECT username FROM Customer WHERE user_id = (?) UNION
        SELECT username FROM Professional WHERE user_id = (?);
    ''', (user_id, user_id )).fetchone()[0]
    cur.close()
    return result

def get_pro_id_by_username(username):
    conn = sqlite3.connect('bilinkedin.db')
    cur = conn.cursor()
    ret = cur.execute('''
        SELECT user_id FROM Professional WHERE username = (?);
    ''', (username, )).fetchone()[0]
    cur.close()
    return ret

def get_cus_id_by_username(username):
    conn = sqlite3.connect('bilinkedin.db')
    cur = conn.cursor()
    ret = cur.execute('''
        SELECT user_id FROM Customer WHERE username = (?);
    ''', (username, )).fetchone()[0]
    cur.close()
    return ret

# -> add_active_user(user_id) - returns the token created
def add_active_user(user_id):  ##assumes a user with that user_id exists
    conn = sqlite3.connect('bilinkedin.db')
    cur = conn.cursor()
    remove_active_user_byid(user_id)  # this removes (logs out) the user if it was already logged in before(aka if it was active)

    candidate_token = secrets.token_urlsafe(16)  ##made these urlsafe just to be safe
    while get_user_id_by_token(candidate_token) != -1:
        candidate_token = secrets.token_urlsafe(16)

    ret = cur.execute('''
		INSERT INTO ActiveUsers(token,user_id) VALUES (?,?);
	''', (candidate_token, user_id))
    conn.commit()
    cur.close()
    return candidate_token

# -> remove_active_user_byid(user_id)
def remove_active_user_byid(user_id):
	conn = sqlite3.connect('bilinkedin.db')
	cur = conn.cursor()
	cur.execute('''DELETE FROM ActiveUsers WHERE ActiveUsers.user_id=(?);''', (user_id,));
	conn.commit()
	cur.close()



# might make this return whether if something was removed or not
def add_professional(username, password, firstname, lastname, email, fields):
    conn = sqlite3.connect('bilinkedin.db')
    cur = conn.cursor()
    cur.execute('''
    	INSERT INTO oyuncakProfessional(user_id, username, password, email, firstname, lastname, balance)
    		VALUES(?, ?, ?, ?, ?, ?, ?);
    ''', (50000, username, password, email, firstname, lastname, 0))
    conn.commit()
    user_id = get_pro_id_by_username(username)
    for field in fields:
        cur.execute('''INSERT INTO ProfessionalField(user_id, field) VALUES(?, ?);''', (user_id, field))
        conn.commit()
    cur.close()



def add_customer(username, password, firstname, lastname, email):
    conn = sqlite3.connect('bilinkedin.db')
    cur = conn.cursor()
    cur.execute('''
    	INSERT INTO oyuncakCustomer(user_id, username, password, email, firstname, lastname, balance)
    		VALUES(?, ?, ?, ?, ?, ?, ?);
    ''', (50000, username, password, email, firstname, lastname, 0))
    cur.close()
    conn.commit()

# returns the user id of user with the given token, -1 if not found
def get_user_id_by_token(token):
    conn = sqlite3.connect('bilinkedin.db')
    cur = conn.cursor()
    ret = cur.execute('''
		SELECT user_id 
		FROM ActiveUsers
		WHERE ActiveUsers.token == ?;
	''', (token,))
    ret = ret.fetchone()
    cur.close()
    return ret[0] if ret != None else -1


##0 firstname 1 lastname 2 username 3 balance 4 avg_rating
# TODO BUYUK SIKINTI !!! en basta professional_avg_rating viewi bos oldugu icin NATURAL JOINledigimiz icin sonuc da bos geliyor
# ayni muhabbet get_customer_profile'da da var
def get_professional_profile(user_id):
    conn = sqlite3.connect('bilinkedin.db')
    cur = conn.cursor()
    professional = cur.execute(''' 
	    SELECT firstname, lastname, username, balance, email
	    FROM Professional 
	    WHERE user_id = (?)
	''', (user_id,)).fetchone()

    avg_rating = cur.execute('''
		SELECT avg_rating FROM professional_avg_ratings WHERE user_id = (?);
	''', (user_id,)).fetchone()
    avg_rating = avg_rating[0] if avg_rating != None else 0
    cur.close()
    return professional, avg_rating


def get_customer_profile(user_id):
    conn = sqlite3.connect('bilinkedin.db')
    cur = conn.cursor()
    customer = cur.execute(''' 
	    SELECT firstname, lastname, username, balance, email
	    FROM Customer 
	    WHERE user_id = (?);
	''', (user_id,)).fetchone()

    avg_rating = cur.execute('''
		SELECT avg_rating FROM customer_avg_ratings WHERE user_id = (?);
	''', (user_id,)).fetchone()
    avg_rating = avg_rating[0] if avg_rating != None else 0
    cur.close()
    return customer, avg_rating


def get_professional_fields(user_id):
    conn = sqlite3.connect('bilinkedin.db')
    cur = conn.cursor()
    ret = cur.execute('''
        SELECT field FROM ProfessionalField WHERE user_id = (?);
    ''', (user_id,)).fetchall()
    cur.close()
    return ret


def update_professional(user_id, email,  username, fields):
    conn = sqlite3.connect('bilinkedin.db')
    cur = conn.cursor()
    if email != '':
        print('email=', email)
        present_email = cur.execute('''
            SELECT email FROM Professional WHERE user_id = (?);
        ''', (user_id, )).fetchone()[0]
        print('present_email=',present_email)
        # to prevent unique constraint error
        if email != present_email:
            cur.execute('''
                UPDATE Professional
                SET email = (?)
                WHERE user_id = (?);
            ''', (email, user_id))
            conn.commit()

    if username != '':
        cur.execute('''
			UPDATE Professional 
			SET username = (?)
			WHERE user_id = (?);
		''', (username, user_id))
        conn.commit()

    cur.execute('''
        DELETE FROM ProfessionalField WHERE user_id = (?);
    ''', (user_id,))
    conn.commit()

    for field in fields:
        cur.execute('''
			INSERT INTO ProfessionalField(user_id, field) 
			VALUES(?, ?); 
		''', (user_id, field))
        conn.commit()
    cur.close()



def update_customer(user_id, email, username):
    conn = sqlite3.connect('bilinkedin.db')
    cur = conn.cursor()
    if email != '':
        present_email = cur.execute('''
            SELECT email FROM Customer WHERE user_id = (?);
        ''', (user_id, )).fetchone()[0]
        # to prevent unique constraint error
        if email != present_email:
            cur.execute('''
                UPDATE Customer
                SET email = (?)
                WHERE user_id = (?);
            ''', (email, user_id))
            conn.commit()
    if username != '':
        cur.execute('''
    		UPDATE Customer
    		SET username = (?)
    		WHERE user_id = (?);
    	''', (username, user_id))
        conn.commit()
    cur.close()


#def add_customer_review(user_id, review_text, rating):
#    conn = sqlite3.connect('bilinkedin.db')
#    cur= conn.cursor()
#    cur.execute('''
#        INSERT INTO CustomerReview(,)
#    ''')

def get_customer_reviews(user_id):
    conn = sqlite3.connect('bilinkedin.db')
    cur = conn.cursor()
    review_ids = cur.execute('''
		SELECT review_id, user_id FROM customer_reviews WHERE user_id = (?);
	''', (user_id,)).fetchall()

    if review_ids != None:
        reviews = []
        for review_id in review_ids:
            review = cur.execute('''SELECT review_text, rating FROM CustomerReview 
                WHERE review_id = (?)''', (review_id[0], )).fetchone()
            reviews.append(review)
        cur.close()
        return reviews, review_ids
    else:
        cur.close()
        return [],[]


def get_professional_reviews(user_id):
    conn = sqlite3.connect('bilinkedin.db')
    cur = conn.cursor()
    review_ids = cur.execute('''
    		SELECT review_id, user_id FROM professional_reviews WHERE user_id = (?);
    	''', (user_id,)).fetchall()

    if review_ids != None:
        reviews = []
        for review_id in review_ids:
            review = cur.execute('''SELECT review_text, rating FROM ProfessionalReview 
                    WHERE review_id = (?)''', (review_id[0],)).fetchone()
            reviews.append(review)
        cur.close()
        return reviews, review_ids
    else:
        cur.close()
        return [], []


def add_announcement(user_id, title, description, start_date, end_date, max_price, location, field):
    conn = sqlite3.connect('bilinkedin.db')
    cur = conn.cursor()
    cur.execute('''
		INSERT INTO JobAnnouncement(user_id, title, description, start_date, end_date, 
			maximum_cost, location, field) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
	''', (user_id, title, description, start_date, end_date, max_price, location, field))
    conn.commit()
    cur.close()


def get_available_jobs(user_id, start_date=None, end_date=None):
    conn = sqlite3.connect('bilinkedin.db')
    cur = conn.cursor()

    if start_date and end_date:
        jobs = cur.execute('''
                    SELECT announcement_id, title, description, start_date, end_date, maximum_cost, location, 
                        JobAnnouncement.field, username 
                    FROM JobAnnouncement, ProfessionalField, Customer 
                    WHERE JobAnnouncement.field = ProfessionalField.field AND
                        JobAnnouncement.user_id = Customer.user_id AND
                        ProfessionalField.user_id = (?) AND 
                        start_date > (?) AND
                        end_date < (?) AND
						announcement_id NOT IN (SELECT announcement_id FROM professional_commissions) AND
						announcement_id NOT IN (SELECT announcement_id FROM pro_offer WHERE user_id=(?))
                    ORDER BY start_date ASC;
                ''', (user_id, start_date, end_date,user_id)).fetchall()
    else:
        jobs = cur.execute('''
            SELECT announcement_id, title, description, start_date, end_date, maximum_cost, location, 
                JobAnnouncement.field, username 
            FROM JobAnnouncement, ProfessionalField, Customer 
            WHERE JobAnnouncement.field = ProfessionalField.field AND
                JobAnnouncement.user_id = Customer.user_id AND
                ProfessionalField.user_id = (?) AND
				announcement_id NOT IN (SELECT announcement_id FROM professional_commissions) AND
				announcement_id NOT IN (SELECT announcement_id FROM pro_offer WHERE user_id=(?))
            ORDER BY start_date ASC;
        ''', (user_id,user_id )).fetchall()

    avg_ratings = []
    for job in jobs:
        user_id = get_cus_id_by_username(job[8])
        avg_rating = cur.execute('''
            SELECT avg_rating FROM customer_avg_ratings WHERE user_id = (?);
        ''', (user_id, )).fetchone()
        avg_rating = avg_rating[0] if avg_rating != None else 0
        avg_ratings.append(avg_rating)
    cur.close()
    return jobs, avg_ratings

# TWEAKED!!
def add_offer(user_id, announcement_id, description, start_date, end_date, price):
    conn = sqlite3.connect('bilinkedin.db')
    cur = conn.cursor()

    cur.execute('''
		INSERT INTO oyuncakOffer(offer_text, start_date, end_date, cost, announcement_id, user_id)
		VALUES(?, ?, ?, ?, ?, ?);
	''', (description, start_date, end_date, price, announcement_id, user_id))
    conn.commit()
    cur.close()


def delete_offer(offer_id):
    conn = sqlite3.connect('bilinkedin.db')
    cur = conn.cursor()
    chat_id = cur.execute('''
        SELECT chat_id FROM Offer WHERE offer_id = (?); 
    ''', (offer_id, )).fetchone()[0]
    cur.execute('''
        DELETE FROM pro_offer WHERE offer_id = (?);
    ''', (offer_id, ))
    conn.commit()
    cur.execute('''
        DELETE FROM OfferChat WHERE chat_id = (?);
    ''', (chat_id, ))
    conn.commit()
    cur.execute('''
        DELETE FROM ChatMessage WHERE chat_id = (?);
    ''', (chat_id, ))
    conn.commit()
    cur.execute('''
        DELETE FROM Offer WHERE offer_id = (?);
    ''', (offer_id, ))
    conn.commit()
    cur.execute('''
        DELETE FROM Chat WHERE chat_id = (?);
    ''', (chat_id, ))
    conn.commit()
    cur.close()



def get_offers_customer(user_id):
    conn = sqlite3.connect('bilinkedin.db')
    cur = conn.cursor()
    offers = cur.execute('''
		SELECT Offer.offer_id, Professional.user_id, Offer.offer_text, Offer.start_date, Offer.end_date, Offer.cost, 
		    Professional.username, JobAnnouncement.announcement_id
		FROM pro_offer, JobAnnouncement, Offer, Professional
		WHERE pro_offer.user_id = Professional.user_id AND 
	        pro_offer.offer_id = Offer.offer_id AND
			JobAnnouncement.announcement_id = pro_offer.announcement_id AND
			JobAnnouncement.user_id = (?) AND
		    Offer.offer_id NOT IN (SELECT offer_id FROM Commission);
	''', (user_id,)).fetchall()

    avg_ratings = []
    for offer in offers:
        avg_rating = cur.execute('''
            SELECT avg_rating FROM professional_avg_ratings WHERE user_id = (?); 
        ''', (offer[1], )).fetchone()
        avg_rating = avg_rating[0] if avg_rating != None else 0
        avg_ratings.append(avg_rating)
    cur.close()
    return offers, avg_ratings

def get_offers_professional(user_id):
    conn = sqlite3.connect('bilinkedin.db')
    cur = conn.cursor()
    offers = cur.execute('''
        SELECT Offer.offer_id, Customer.user_id, Offer.offer_text, Offer.start_date, Offer.end_date, Offer.cost, 
            Customer.username, JobAnnouncement.announcement_id
        FROM pro_offer, JobAnnouncement, Offer, Customer
        WHERE pro_offer.user_id = (?) AND
            pro_offer.offer_id = Offer.offer_id AND
            JobAnnouncement.announcement_id = pro_offer.Announcement_id AND
            JobAnnouncement.user_id = Customer.user_id AND
            Offer.offer_id NOT IN (SELECT offer_id FROM Commission);
    ''', (user_id, )).fetchall()

    avg_ratings = []
    for offer in offers:
        avg_rating = cur.execute('''
            SELECT avg_rating FROM customer_avg_ratings WHERE user_id = (?); 
        ''', (offer[1], )).fetchone()
        avg_rating = avg_rating[0] if avg_rating != None else 0
        avg_ratings.append(avg_rating)
    cur.close()
    return offers, avg_ratings

def add_to_balance(user_id, amount, role):
    conn = sqlite3.connect('bilinkedin.db')
    cur = conn.cursor()
    if role == 'professional':
        cur.execute('''
            UPDATE Professional
            SET balance = balance + (?)
            WHERE user_id = (?);
        ''', (amount, user_id))
        conn.commit()
    if role == 'customer':
        cur.execute('''
            UPDATE Customer
            SET balance = balance + (?)
            WHERE user_id = (?);
        ''', (amount, user_id))
        conn.commit()
    cur.close()

def get_announcement_by_id(announcement_id):
    conn = sqlite3.connect('bilinkedin.db')
    cur = conn.cursor()
    announcement = cur.execute('''
        SELECT * FROM JobAnnouncement WHERE announcement_id = (?);
    ''', (announcement_id, )).fetchone()
    announcer = cur.execute('''
        SELECT Customer.user_id, username FROM JobAnnouncement, Customer WHERE announcement_id = (?); 
    ''', (announcement_id, )).fetchone()
    avg_rating = cur.execute('''
        SELECT avg_rating FROM customer_avg_ratings WHERE user_id = (?);
    ''', (announcer[0], )).fetchone()
    avg_rating = avg_rating[0] if avg_rating != None else 0
    cur.close()
    return announcement, announcer, avg_rating

def get_customer_announcements(user_id):
    conn = sqlite3.connect('bilinkedin.db')
    cur = conn.cursor()
    announcements = cur.execute('''
        SELECT * FROM JobAnnouncement WHERE user_id = (?);    
    ''', (user_id, )).fetchall()
    cur.close()
    return announcements


def get_offer_chat(offer_id):
    conn = sqlite3.connect('bilinkedin.db')
    cur = conn.cursor()
    chat_id = cur.execute('''
        SELECT chat_id FROM Offer WHERE offer_id = (?);
    ''', (offer_id, )).fetchone()[0]
    messages = cur.execute('''
        SELECT * FROM ChatMessage WHERE chat_id = (?);
    ''', (chat_id, )).fetchall()
    cur.close()
    return messages

def add_to_offer_chat(user_id, offer_id, message_text, date_and_time):
    conn = sqlite3.connect('bilinkedin.db')
    cur = conn.cursor()
    chat_id = cur.execute('''SELECT chat_id FROM Offer WHERE offer_id = (?);''', (offer_id, )).fetchone()[0]

    cur.execute('''INSERT INTO ChatMessage(chat_id, user_id, message_text, date_and_time)
                    VALUES(?, ?, ?, ?)''', (chat_id, user_id, message_text, date_and_time))
    conn.commit()
    cur.close()

def add_commission(user_id, offer_id):
    conn = sqlite3.connect('bilinkedin.db')
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO oyuncakCommission(offer_id)
            VALUES(?);
    ''', (offer_id, ))
    conn.commit()
    announcement_id = \
        cur.execute('''SELECT announcement_id FROM pro_offer WHERE offer_id = (?);''',(offer_id,)).fetchone()[0]
    # TODO announcement and offer cannot be deleted because the commission will be unreachable if we do that
    #delete_offer(offer_id)
    #cur.execute('''
    #    DELETE FROM JobAnnouncement WHERE announcement_id = (?)
    #''', (announcement_id, ))
    #conn.commit()
    cur.close()

def get_professional_commissions(user_id):
    conn = sqlite3.connect('bilinkedin.db')
    cur = conn.cursor()

    commission_ids = cur.execute('''
        SELECT commission_id 
        FROM Commission, pro_offer
        WHERE pro_offer.offer_id = Commission.offer_id AND
              pro_offer.user_id = (?);
    ''', (user_id, )).fetchall()

    commissions = []
    announcers = []
    avg_ratings = []
    for commission_id in commission_ids:
        result = cur.execute('''
            SELECT Commission.commission_id, JobAnnouncement.title, Commission.status, 
                Commission.start_date, Commission.end_date, Commission.cost, JobAnnouncement.location,
                 Offer.offer_text, JobAnnouncement.announcement_id
            FROM Commission, Offer, JobAnnouncement, pro_offer
            WHERE Commission.offer_id = Offer.offer_id AND
                pro_offer.offer_id = Offer.offer_id AND
                pro_offer.announcement_id = JobAnnouncement.announcement_id AND
                Commission.commission_id = (?);
        ''', (commission_id[0], )).fetchone()
        commissions.append(result)
        announcement_id = result[8]
        result = cur.execute('''
            SELECT Customer.user_id, Customer.username FROM JobAnnouncement, Customer
            WHERE Customer.user_id = JobAnnouncement.user_id AND
                JobAnnouncement.announcement_id = (?); 
        ''', (announcement_id, )).fetchone()
        announcers.append(result)
        cus_user_id = result[0]
        result = cur.execute('''
            SELECT avg_rating FROM customer_avg_ratings WHERE user_id = (?);
        ''', (cus_user_id, )).fetchone()
        avg_rating = result[0] if result != None else 0
        avg_ratings.append(avg_rating)
    cur.close()
    return commissions, announcers, avg_ratings

def get_customer_commissions(user_id):
    conn = sqlite3.connect('bilinkedin.db')
    cur = conn.cursor()

    commission_ids = cur.execute('''
        SELECT commission_id 
        FROM Commission, pro_offer, JobAnnouncement
        WHERE pro_offer.offer_id = Commission.offer_id AND
              pro_offer.announcement_id = JobAnnouncement.announcement_id AND
              JobAnnouncement.user_id = (?);
    ''', (user_id, )).fetchall()

    commissions = []
    announcers = []
    avg_ratings = []
    for commission_id in commission_ids:
        result = cur.execute('''
            SELECT Commission.commission_id, JobAnnouncement.title, Commission.status, 
                Commission.start_date, Commission.end_date, Commission.cost, JobAnnouncement.location,
                 Offer.offer_text, JobAnnouncement.announcement_id
            FROM Commission, Offer, JobAnnouncement, pro_offer
            WHERE Commission.offer_id = Offer.offer_id AND
                pro_offer.offer_id = Offer.offer_id AND
                pro_offer.announcement_id = JobAnnouncement.announcement_id AND
                Commission.commission_id = (?);
        ''', (commission_id[0], )).fetchone()
        commissions.append(result)
        announcement_id = result[8]
        result = cur.execute('''
            SELECT Professional.user_id, Professional.username 
            FROM JobAnnouncement, Professional, pro_offer, Commission
            WHERE Professional.user_id = pro_offer.user_id AND
                pro_offer.announcement_id = JobAnnouncement.announcement_id AND
                pro_offer.offer_id = Commission.commission_id AND
                JobAnnouncement.announcement_id = (?); 
        ''', (announcement_id, )).fetchone()
        announcers.append(result)
        pro_user_id = result[0]
        result = cur.execute('''
            SELECT avg_rating FROM professional_avg_ratings WHERE user_id = (?);
        ''', (pro_user_id, )).fetchone()
        avg_rating = result[0] if result != None else 0
        avg_ratings.append(avg_rating)
    cur.close()
    return commissions, announcers, avg_ratings

def get_commission_chat(commission_id):
    conn = sqlite3.connect('bilinkedin.db')
    cur = conn.cursor()
    chat_id = cur.execute('''
        SELECT chat_id FROM Commission WHERE commission_id = (?);
    ''', (commission_id, )).fetchone()[0]
    messages = cur.execute('''
        SELECT * FROM ChatMessage WHERE chat_id = (?);
    ''', (chat_id, )).fetchall()
    cur.close()
    return messages

def add_to_commission_chat(user_id, commission_id, message_text, date_and_time):
    conn = sqlite3.connect('bilinkedin.db')
    cur = conn.cursor()

    chat_id = cur.execute('''SELECT chat_id FROM Commission WHERE commission_id = (?);''', (commission_id, )).fetchone()[0]

    cur.execute('''INSERT INTO ChatMessage(chat_id, user_id, message_text, date_and_time)
                    VALUES(?, ?, ?, ?)''', (chat_id, user_id, message_text, date_and_time))
    conn.commit()
    cur.close()

def search_job(keyword):
    conn = sqlite3.connect('bilinkedin.db')
    cur = conn.cursor()

    jobs = cur.execute('''  
        SELECT announcement_id 
        FROM JobAnnouncement
        WHERE title LIKE (?);
    ''', ('%' + keyword + '%', )).fetchall()

    return jobs
	
	
	
def commission_mark_complete_cus(commission_id):
	conn = sqlite3.connect('bilinkedin.db')
	cur = conn.cursor()
	
	status = cur.execute('''
		SELECT status FROM Commission WHERE commission_id = (?);
	''',(commission_id,)).fetchone()[0]
	
	if status == "active":
		cur.execute('''
			UPDATE Commission SET status = 'marked_cus' WHERE commission_id = (?);
		''',(commission_id,))
		conn.commit()
	else:
		cur.execute('''
			UPDATE Commission SET status = 'complete' WHERE commission_id = (?);
		''',(commission_id,))
		conn.commit()
	cur.close()
	
def commission_mark_complete_pro(commission_id):
	conn = sqlite3.connect('bilinkedin.db')
	cur = conn.cursor()
	
	status = cur.execute('''
		SELECT status FROM Commission WHERE commission_id = (?);
	''',(commission_id,)).fetchone()[0]
	
	if status == "active":
		cur.execute('''
			UPDATE Commission SET status = 'marked_pro' WHERE commission_id = (?);
		''',(commission_id,))
		conn.commit()
	else:
		cur.execute('''
			UPDATE Commission SET status = 'complete' WHERE commission_id = (?);
		''',(commission_id,))
		conn.commit()
	cur.close()
	
	
def add_review_to_customer(commission_id,rating,review_text):
	conn = sqlite3.connect('bilinkedin.db')
	cur = conn.cursor()
	
	cur.execute('''
		INSERT INTO CustomerReview(commission_id,rating,review_text)
			VALUES(?,?,?);
	''',(commission_id,rating,review_text))
	conn.commit()
	cur.close()

def add_review_to_professional(commission_id,rating,review_text):
	conn = sqlite3.connect('bilinkedin.db')
	cur = conn.cursor()
	
	cur.execute('''
		INSERT INTO ProfessionalReview(commission_id,rating,review_text)
			VALUES(?,?,?);
	''',(commission_id,rating,review_text))
	conn.commit()
	cur.close()
	
	
	
	
	
	
def get_pro_review_id(commission_id):
	conn = sqlite3.connect('bilinkedin.db')
	cur = conn.cursor()
	review_id = cur.execute('''SELECT review_id FROM ProfessionalReview WHERE commission_id = (?);
	''', (commission_id, )).fetchone()
	review_id = review_id[0] if review_id != None else 0
	return review_id

def get_cus_review_id(commission_id):
	conn = sqlite3.connect('bilinkedin.db')
	cur = conn.cursor()
	review_id = cur.execute('''SELECT review_id FROM CustomerReview WHERE commission_id = (?);
	''', (commission_id, )).fetchone()
	review_id = review_id[0] if review_id != None else 0
	return review_id

	
	
	
	
	
	
	
	
	
	
	
	

	