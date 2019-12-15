import sqlite3

conn = sqlite3.connect("bilinkedin.db")
cur = conn.cursor()


cur.execute('''DROP VIEW professional_commissions;''')
cur.execute('''
	CREATE VIEW IF NOT EXISTS professional_commissions AS 
	SELECT pro_offer.user_id AS user_id, Commission.commission_id AS commission_id
	FROM pro_offer, Offer, Commission
	WHERE Offer.offer_id = pro_offer.offer_id AND
		Commission.offer_id = Offer.offer_id
	;
''')

