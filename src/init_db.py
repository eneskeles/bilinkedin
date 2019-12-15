import sqlite3
from datetime import date

conn = sqlite3.connect('bilinkedin.db')
cur = conn.cursor()

cur.execute('''
    CREATE TABLE IF NOT EXISTS User (
        user_id   INTEGER PRIMARY KEY AUTOINCREMENT
    )
''')

cur.execute('''
    CREATE TABLE IF NOT EXISTS Customer (
        user_id     INT PRIMARY KEY,
        username    VARCHAR(32) NOT NULL,
        password    VARCHAR(32) NOT NULL, 
        email       VARCHAR(64) NOT NULL UNIQUE, 
        firstname   VARCHAR(32) NOT NULL, 
        lastname    VARCHAR(32) NOT NULL, 
        balance     FLOAT       NOT NULL, 
        FOREIGN KEY(user_id) REFERENCES User
    )
''')

cur.execute('''
    CREATE TABLE IF NOT EXISTS Professional (
        user_id    INT PRIMARY KEY,
        username   VARCHAR(32) NOT NULL,
        password   VARCHAR(32) NOT NULL, 
        email      VARCHAR(64) NOT NULL UNIQUE, 
        firstname  VARCHAR(32) NOT NULL, 
        lastname   VARCHAR(32) NOT NULL, 
        balance    FLOAT       NOT NULL,
        FOREIGN KEY(user_id) REFERENCES User
    )
''')

cur.execute(''' 
    CREATE TABLE IF NOT EXISTS ProfessionalField (
        user_id  INT NOT NULL, 
        field    VARCHAR(32) NOT NULL, 
        PRIMARY KEY(user_id, field),
        FOREIGN KEY(user_id) REFERENCES Professional
    )
''')

cur.execute('''
    CREATE TABLE IF NOT EXISTS CustomerSupport (
        user_id	INTEGER PRIMARY KEY,
        username   VARCHAR(32) NOT NULL,
        password   VARCHAR(32) NOT NULL, 
        email      VARCHAR(64) NOT NULL UNIQUE, 
        firstname  VARCHAR(32) NOT NULL, 
        lastname   VARCHAR(32) NOT NULL, 
        balance    FLOAT       NOT NULL,
        FOREIGN KEY(user_id) REFERENCES User
    )
''')

cur.execute(''' 
    CREATE TABLE IF NOT EXISTS JobAnnouncement (
        announcement_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id           INT           NOT NULL, 
        title 		      VARCHAR(32)   NOT NULL,
        description       VARCHAR(256)  NOT NULL, 
        start_date 	      DATE,
        end_date		  DATE,
        maximum_cost 	  FLOAT, 
        location 		  VARCHAR(128)  NOT NULL, 
        field 		  VARCHAR(32)   NOT NULL,
        FOREIGN KEY(user_id) REFERENCES Customer  
    )
''')

cur.execute(''' 
    CREATE TABLE IF NOT EXISTS Offer ( 
        offer_id     INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id      INT UNIQUE   NOT NULL,  
        offer_text   VARCHAR(256) NOT NULL, 
        start_date   DATE, 
        end_date     DATE, 
        cost         FLOAT        NOT NULL,
        FOREIGN KEY(chat_id) REFERENCES OfferChat
    )
''')

# Changed primary key
cur.execute('''
    CREATE TABLE IF NOT EXISTS pro_offer (
        offer_id 		 INTEGER NOT NULL,
        user_id 		 INT NOT NULL, 
        announcement_id  INT NOT NULL,
        PRIMARY KEY(user_id, announcement_id),
        FOREIGN KEY(offer_id)        REFERENCES Offer,
        FOREIGN KEY(user_id)         REFERENCES Professional, 
        FOREIGN KEY(announcement_id) REFERENCES JobAnnouncement
    )
''')

cur.execute(''' 
    CREATE TABLE IF NOT EXISTS Commission (
        commission_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        offer_id 		INT UNIQUE   NOT NULL,
        chat_id 		INT UNIQUE   NOT NULL,
        start_date      DATE,
        end_date 		DATE, 
        cost 			FLOAT        NOT NULL, 
        status 		VARCHAR(32)  NOT NULL, 
        FOREIGN KEY(offer_id) REFERENCES Offer,
        FOREIGN KEY(chat_id)  REFERENCES CommissionChat
    )
''')

cur.execute('''
    CREATE TABLE IF NOT EXISTS ProfessionalReview (
        review_id  	INTEGER PRIMARY KEY AUTOINCREMENT, 
        commission_id   INT UNIQUE    NOT NULL, 
        rating 		FLOAT         NOT NULL, 
        review_text 	VARCHAR(512)  NOT NULL,
        FOREIGN KEY(commission_id) REFERENCES Commission
    )
''')

cur.execute(''' 
    CREATE TABLE IF NOT EXISTS CustomerReview (
        review_id  	INTEGER PRIMARY KEY AUTOINCREMENT, 
        commission_id   INT UNIQUE    NOT NULL, 
        rating 		FLOAT         NOT NULL, 
        review_text 	VARCHAR(512)  NOT NULL,
        FOREIGN KEY(commission_id) REFERENCES Commission
    )
''')

cur.execute(''' 
    CREATE TABLE IF NOT EXISTS Ticket (
        ticket_id 		INTEGER PRIMARY KEY AUTOINCREMENT, 
        commission_id   INT          NOT NULL, 
        title 		VARCHAR(32)  NOT NULL,
        description 	VARCHAR(512) NOT NULL, 
        FOREIGN KEY(commission_id) REFERENCES Commission
    )
''')

# Primary key changed.
cur.execute('''
    CREATE TABLE IF NOT EXISTS ticket_chat (
        ticket_id   INT UNIQUE NOT NULL,
        chat_id     INT UNIQUE NOT NULL, 
        user_id     INT, 
        PRIMARY KEY(chat_id, user_id),
        FOREIGN KEY(ticket_id) REFERENCES Ticket,
        FOREIGN KEY(chat_id)   REFERENCES TicketChat,
        FOREIGN KEY(user_id)   REFERENCES CustomerSupport
    )
''')

cur.execute('''
    CREATE TABLE IF NOT EXISTS Chat (
	    chat_id INTEGER PRIMARY KEY AUTOINCREMENT
    )
''')

cur.execute(''' 
    CREATE TABLE IF NOT EXISTS CommissionChat (
        chat_id INT PRIMARY KEY,
        FOREIGN KEY(chat_id) REFERENCES Chat
    )
''')

cur.execute(''' 
    CREATE TABLE IF NOT EXISTS TicketChat (
        chat_id INT PRIMARY KEY,
        FOREIGN KEY(chat_id) REFERENCES Chat
    )
''')

cur.execute(''' 
    CREATE TABLE IF NOT EXISTS OfferChat (
        chat_id INT PRIMARY KEY,
        FOREIGN KEY(chat_id) REFERENCES Chat
    )
''')

cur.execute('''
    CREATE TABLE IF NOT EXISTS ChatMessage (
        message_id    INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id       INT          NOT NULL, 
        user_id       INT          NOT NULL, 
        message_text  VARCHAR(256) NOT NULL, 
        date_and_time DATETIME     NOT NULL, 
        FOREIGN KEY(chat_id) REFERENCES Chat, 
        FOREIGN KEY(user_id) REFERENCES User
    )
''')

# holds the active users
cur.execute(''' 
    CREATE TABLE IF NOT EXISTS ActiveUsers (
        token       VARCHAR(128) PRIMARY KEY,
        user_id     INTEGER     NOT NULL UNIQUE, 
        FOREIGN KEY(user_id) REFERENCES User
    ) 
''')

cur.execute('''
	CREATE VIEW IF NOT EXISTS professional_commissions AS 
	SELECT pro_offer.user_id AS user_id, Commission.commission_id AS commission_id, pro_offer.announcement_id as announcement_id
	FROM pro_offer , Offer , Commission
	WHERE Offer.offer_id = pro_offer.offer_id AND
		Commission.offer_id = Offer.offer_id
	;
''')


cur.execute('''
	CREATE VIEW IF NOT EXISTS customer_commissions AS 
	SELECT JobAnnouncement.user_id AS user_id,
		Commission.commission_id AS commission_id, pro_offer.announcement_id as announcement_id
	FROM JobAnnouncement, pro_offer, Offer, Commission
	WHERE pro_offer.announcement_id =
		JobAnnouncement.announcement_id AND
		Offer.offer_id = pro_offer.offer_id AND
		Commission.offer_id = Offer.offer_id
	;
''')


cur.execute('''
	CREATE VIEW IF NOT EXISTS professional_avg_ratings AS 
	SELECT professional_commissions.user_id AS user_id,
		AVG(ProfessionalReview.rating) AS avg_rating
	FROM professional_commissions, ProfessionalReview
	WHERE ProfessionalReview.commission_id =
		professional_commissions.commission_id
	GROUP BY professional_commissions.user_id
	;
''')

cur.execute('''
	CREATE VIEW IF NOT EXISTS customer_avg_ratings AS 
	SELECT customer_commissions.user_id AS user_id,
		AVG(CustomerReview.rating) AS avg_rating
	FROM customer_commissions, CustomerReview
	WHERE CustomerReview.commission_id =
	customer_commissions.commission_id
	GROUP BY customer_commissions.user_id
	;
''')

cur.execute('''
	CREATE VIEW IF NOT EXISTS professional_reviews AS 
	SELECT professional_commissions.user_id AS user_id,
		ProfessionalReview.review_id AS review_id
	FROM professional_commissions, ProfessionalReview
	WHERE ProfessionalReview.commission_id =
		professional_commissions.commission_id
	;
''')



cur.execute('''
	CREATE VIEW IF NOT EXISTS customer_reviews AS 
	SELECT customer_commissions.user_id AS user_id,
		CustomerReview.review_id AS review_id
	FROM customer_commissions, CustomerReview
	WHERE CustomerReview.commission_id =
		customer_commissions.commission_id
	;
''')



cur.execute('''
	CREATE VIEW IF NOT EXISTS professional_tickets AS 
	SELECT professional_commissions.user_id AS user_id,
		Ticket.ticket_id as ticket_id
	FROM professional_commissions, Ticket
	WHERE Ticket.commission_id =
		professional_commissions.commission_id
	;
''')



cur.execute('''
	CREATE VIEW IF NOT EXISTS customer_tickets AS 
	SELECT customer_commissions.user_id AS user_id, 
	    Ticket.ticket_id AS ticket_it
	FROM customer_commissions, Ticket
	WHERE Ticket.commission_id =
		customer_commissions.commission_id
	;
''')

cur.execute('''
	CREATE VIEW IF NOT EXISTS oyuncakProfessional AS
	SELECT * 
	FROM Professional
	;
''')

cur.execute('''
	CREATE VIEW IF NOT EXISTS oyuncakCustomer AS
	SELECT * 
	FROM Customer
	;
''')

cur.execute('''
    CREATE VIEW IF NOT EXISTS oyuncakCommission AS
    SELECT * 
    FROM Commission
''')

cur.execute('''
    CREATE VIEW IF NOT EXISTS oyuncakOffer AS 
    SELECT  offer_text, start_date, end_date, cost, pro_offer.announcement_id AS announcement_id, user_id
    FROM Offer, pro_offer
    ;
''')



cur.execute('''
    CREATE TRIGGER IF NOT EXISTS add_commission INSTEAD OF INSERT ON oyuncakCommission
    BEGIN
        INSERT INTO Chat(chat_id) VALUES(NULL);
        INSERT INTO CommissionChat(chat_id) VALUES((SELECT MAX(chat_id) FROM Chat));
        INSERT INTO Commission(offer_id, chat_id, start_date, end_date, cost, status) 
            VALUES(NEW.offer_id, (SELECT MAX(chat_id) FROM CommissionChat), 
            (SELECT start_date FROM Offer WHERE offer_id = NEW.offer_id), 
            (SELECT end_date FROM Offer WHERE offer_id = NEW.offer_id), 
            (SELECT cost FROM Offer WHERE offer_id = NEW.offer_id), 'active');
    END
''')
cur.execute('''
    CREATE TRIGGER IF NOT EXISTS add_offer INSTEAD OF INSERT ON oyuncakOffer
    BEGIN
        INSERT INTO Chat(chat_id) VALUES (NULL);
        INSERT INTO OfferChat(chat_id) VALUES ((SELECT MAX(chat_id) FROM Chat)); 
        INSERT INTO Offer(chat_id, offer_text, start_date, end_date, cost)
            VALUES((SELECT MAX(chat_id) FROM OfferChat), NEW.offer_text, NEW.start_date, NEW.end_date, NEW.cost);
        INSERT INTO pro_offer(announcement_id, user_id, offer_id) 
            VALUES(NEW.announcement_id, NEW.user_id, (SELECT MAX(offer_id) FROM Offer));
    END
''')

cur.execute('''
	CREATE TRIGGER IF NOT EXISTS add_professional INSTEAD OF INSERT ON oyuncakProfessional
	BEGIN
		INSERT INTO User(user_id) VALUES (NULL);
		INSERT INTO Professional(user_id, username, password, email, firstname, lastname, balance)
		  VALUES((SELECT MAX(user_id) FROM User), NEW.username, NEW.password,
				 NEW.email, NEW.firstname, NEW.lastname, NEW.balance);
	END
''')

cur.execute('''
	CREATE TRIGGER IF NOT EXISTS add_customer INSTEAD OF INSERT ON oyuncakCustomer
	BEGIN
		INSERT INTO User(user_id) VALUES (NULL);
		INSERT INTO Customer(user_id, username, password, email, firstname, lastname, balance)
		  VALUES((SELECT MAX(user_id) FROM User), NEW.username, NEW.password,
				 NEW.email, NEW.firstname, NEW.lastname, NEW.balance);
	END
''')


cur.execute('''
    CREATE INDEX IF NOT EXISTS announcement_start_date ON JobAnnouncement(start_date);
''')

cur.execute('''
    CREATE INDEX IF NOT EXISTS offer_start_date ON Offer(start_date);
''')

cur.execute('''
    CREATE INDEX IF NOT EXISTS commission_start_date ON Commission(start_date);
''')

# ## REPORTS
# # AVG, MAX, MIN cost of completed commissions this month
# cur.execute('''
    # SELECT status, AVG(cost) AS avg_cost, MAX(cost) AS max_cost, MIN(cost) AS min_cost
    # FROM Commission
    # WHERE start_date > (?)
    # GROUP BY status
# ''', (datetime.date(2018, 1, 1), )).fetchall()

# # AVG duration of offers this month
# cur.execute('''
    # SELECT AVG(end_date - start_date) AS avg_duration
    # FROM Offer
    # WHERE start_date > (?)
# ''', (datetime.date(2018, 1, 1), )).fetchone()

# cur.execute('''
    # SELECT field, COUNT(field)
    # FROM JobAnnouncement
    # GROUP BY field
# ''')









conn.commit()
