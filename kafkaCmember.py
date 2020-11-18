#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from confluent_kafka import Consumer, KafkaException, KafkaError
import sys
import pymysql,redis
import time



# 用來接收從Consumer instance發出的error訊息
def error_cb(err):
    print('Error: %s' % err)


# 轉換msgKey或msgValue成為utf-8的字串
def try_decode_utf8(data):
    if data:
        return data.decode('utf-8')
    else:
        return None


# 當發生Re-balance時, 如果有partition被assign時被呼叫
def print_assignment(consumer, partitions):
    result = '[{}]'.format(','.join([p.topic + '-' + str(p.partition) for p in partitions]))
    print('Setting newly assigned partitions:', result)


# 當發生Re-balance時, 之前被assigned的partition會被移除
def print_revoke(consumer, partitions):
    result = '[{}]'.format(','.join([p.topic + '-' + str(p.partition) for p in partitions]))
    print('Revoking previously assigned partitions: ' + result)


def consumerMember():
    # 步驟1.設定要連線到Kafka集群的相關設定
    # Consumer configuration
    # See https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
    props = {
        'bootstrap.servers': 'kafka:29092',         # Kafka集群在那裡? (置換成要連接的Kafka集群)
        'group.id': 'iii',                             # ConsumerGroup的名稱 (置換成你/妳的學員ID)
        'auto.offset.reset': 'earliest',               # Offset從最前面開始
        'error_cb': error_cb                           # 設定接收error訊息的callback函數
    }

    # 步驟2. 產生一個Kafka的Consumer的實例
    consumer = Consumer(props)
    # 步驟3. 指定想要訂閱訊息的topic名稱
    topicName = 'members'
    # 步驟4. 讓Consumer向Kafka集群訂閱指定的topic
    consumer.subscribe([topicName], on_assign=print_assignment, on_revoke=print_revoke)

    # 步驟5. 持續的拉取Kafka有進來的訊息
    try:
        while True:
            # 請求Kafka把新的訊息吐出來
            records = consumer.consume(num_messages=500, timeout=1.0)  # 批次讀取
            if records is None:
                continue

            for record in records:
                # 檢查是否有錯誤
                if record is None:
                    continue
                if record.error():
                    # Error or event
                    if record.error().code() == KafkaError._PARTITION_EOF:
                        print('')
                        # End of partition event
                        # sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                        #                 (record.topic(), record.partition(), record.offset()))
                    else:
                        # Error
                        raise KafkaException(record.error())
                else:
                    # ** 在這裡進行商業邏輯與訊息處理 **
                    # 取出相關的metadata
                    topic = record.topic()
                    partition = record.partition()
                    offset = record.offset()
                    timestamp = record.timestamp()
                    # 取出msgKey與msgValue
                    msgKey = try_decode_utf8(record.key())
                    msgValue = try_decode_utf8(record.value())

                    myValue = msgValue.split(',')

                    # print(myValue)
                    # print(myValue[0])

                    # 秀出metadata與msgKey & msgValue訊息
                    print('%s-%d-%d : (%s)' % (topic, partition, offset, myValue))

                    #連接mysql
                    host = 'mysql'
                    port = 3306
                    user = 'root'
                    passwd = 'iii'
                    db = 'capstone'
                    charset = 'utf8mb4'
                    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset=charset)
                    print('successfully connected')

                    r = redis.Redis(host='redis', port=6379, password='iii', decode_responses=True)

                    cursor = conn.cursor()

                    try:
                        if  myValue[0] == 'INSER':
                            sql = '''
                                    INSERT INTO members (userID, name, joindate)
                                    VALUES ('{:s}','{:s}','{:s}');
                                '''.format(str(myValue[1]), str(myValue[2]), str(myValue[3]))

                            cursor.execute(sql)

                            conn.commit()

                            conn.close()

                    except pymysql.err.IntegrityError:

                        print('會員已經存在')

                    if myValue[0]  == 'UPDATE':

                        sql = '''UPDATE members
                                SET name = '{}', email = '{}', gender = {}, age = {}, height = {}, weight = {}, activity_level = {}, like_ingredient = '{}', dislike_ingredient = '{}', bmr = {}, tdee = {}
                                WHERE userID = '{}';'''.format(str(myValue[1]), str(myValue[2]), int(myValue[3]),int(myValue[4]),float(myValue[5]),float(myValue[6]),int(myValue[7]), str(myValue[8]), str(myValue[9]),float(myValue[10]),float(myValue[11]),str(myValue[12]))

                        # print(sql)

                        cursor.execute(sql)

                        conn.commit()

                        conn.close()

                        r.getset("{}".format(str(myValue[12])),"('{}', '{}', {}, {}, {}, {}, {}, '{}', '{}', {}, {})".format(str(myValue[1]), str(myValue[2]), int(myValue[3]),int(myValue[4]),float(myValue[5]),float(myValue[6]),int(myValue[7]), str(myValue[8]), str(myValue[9]),float(myValue[10]),float(myValue[11])))

    except KeyboardInterrupt as e:
        sys.stderr.write('Aborted by user\n')
    except Exception as e:
        sys.stderr.write(str(e))

    finally:
        # 步驟6.關掉Consumer實例的連線
        consumer.close()


if __name__ == '__main__':
    while True:
        try:
            consumerMember()
        except Exception as ex:
            print(ex)
            time.sleep(2)
            continue
