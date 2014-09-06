import MySQLdb


def match (id, newr_gender, newr_pref, newr_money)
	db=_mysql.connect("localhost","joebob","moonpie","thangs")

	get_port = db.cursor()
	get_port.execute("""SELECT id FROM matches WHERE gender = %s AND price = %s;""", (newr_pref, newr_money, ))
	
	row = get_port.fetchone()
	
	if row is not None:
		# call 
	else
	
	
	
