import redis
import pymysql


r = redis.Redis(host='redis', port=6379, password='iii', decode_responses=True)

host = 'mysql'
port = 3306
user = 'root'
passwd = 'iii'
db = 'capstone'
conn = pymysql.connect(host = host, port = port, user = user, passwd = passwd, db = db, charset = 'utf8')
cursor = conn.cursor()

target = ['tricep','back','leg','ab','chest','shoulder']

frequency = [1,2,3,4,5,6,7]


for i in range(len(target)):
    for j in range(len(frequency)):

        sql = '''SELECT url, img_url, title
        from workout_plans
        where target = "{}" AND frequency = "{}" ;'''.format(str(target[i]), frequency[j])
        cursor.execute(sql)
        data = cursor.fetchall()
        # data = list(data)
        # print(data)
        data1 = []

        for v in range(len(data)):
            data1.append(data[v])
            data1.append('#')
        # print(data1)

        r.hmset("{}".format(target[i]), {"{}".format(frequency[j]): "{}".format(data1)})

        # print(target[i],frequency[j],data)

        # set = "'{}','{}','{}'".format(target[i], frequency[j], data)

        # print(target[i],frequency[j],data)

        # r.hset('{}'.format(target[i]),'{}'.format(frequency[j]),'{}'.format(data))






