import redis
import pymysql

def redisMember(userID):
    try:
        r = redis.Redis(host='192.168.1.37', port = 6379,password = 'iii', decode_responses = True)

        data = r.get('{}'.format(userID))

        return data

    except:

        host = '192.168.1.37'
        port = 3307
        user = 'root'
        passwd = 'iii'
        db = 'capstone'
        conn = pymysql.connect(host = host, port = port, user = user, passwd = passwd, db = db, charset = 'utf8')
        cursor = conn.cursor()

        sql = '''SELECT name,email,gender,age,height,weight,activity_level,like_ingredient,dislike_ingredient,bmr,tdee
                        from members where userID = "{}";'''.format(userID)

        cursor.execute(sql)

        data = cursor.fetchall()

        print(data)

                #prefered_ingred = (data[0][0]).split()
        cursor.close()

        conn.close()

        r = redis.Redis(host='192.168.1.37', port = 6379,password = 'iii', decode_responses = True)

        r.set('{}'.format(userID),'{}'.format(data[0]),ex = 60,nx = True)

        data = r.get('{}'.format(userID))

        print(data)

        return data


if __name__ == '__main__':
    redisMember('Uc767b83a8de8b6656f8da4b8405dde3f')




