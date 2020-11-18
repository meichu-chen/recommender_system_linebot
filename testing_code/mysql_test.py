import pymysql, time
start_time = time.time()
#import recipe_recommend.find_recipe_user_preference as rfp

# pymysql設定資料庫連線設定
host = 'mysql'
port = 3306
user = 'root'
passwd = 'iii'
db = 'capstone'


conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db)
cursor = conn.cursor()

userID = 'U23129823166ce74f47f7a8070e24e7ab'

sql = """SELECT * FROM recipe_favorite WHERE userID='{}'""".format(userID)

cursor.execute(sql)

data = cursor.fetchall()
print(data)
# prefered_ingred = (data[0][0]).split()
# print(prefered_ingred)

cursor.close()
conn.close()

# recommend_result = rfp.main(prefered_ingred)
# print(recommend_result)
# print(recommend_result[0][1][2])
# print(recommend_result[0][1][1])
# print(type(recommend_result[0]))
# print("--- spend %s seconds ---" % (time.time() - start_time))
