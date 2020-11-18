import redis
import pymysql

def redisMember(userID):

    #連接redis
    r = redis.Redis(host = 'redis', port = 6379, password = 'iii', decode_responses = True)

    data = r.get('{}'.format(userID))


    if data != None:

#        print(data)

        return data

    else:
        # 連接mysql
        host = 'mysql'
        port = 3306
        user = 'root'
        passwd = 'iii'
        db = 'capstone'
        conn = pymysql.connect(host = host, port = port, user = user, passwd = passwd, db = db, charset = 'utf8')
        cursor = conn.cursor()

        sql = '''SELECT name,email,gender,age,height,weight,activity_level,like_ingredient,dislike_ingredient,bmr,tdee
                    from members where userID = "{}";'''.format(userID)

        cursor.execute(sql)

        data = cursor.fetchall()

        # print(data)

        cursor.close()

        conn.close()

        r.set('{}'.format(userID),'{}'.format(data[0]),ex = 60,nx = True)

        data = r.get('{}'.format(userID))

        # print(data)

        return data


if __name__ == '__main__':
    redisMember()




