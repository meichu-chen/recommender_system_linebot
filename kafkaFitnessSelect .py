from confluent_kafka import Producer
import sys
import time
import random
import pymysql
# 用來接收從Consumer instance發出的error訊息
def error_cb(err):
    print('Error: %s' % err)

# 主程式進入點
def memberSelect(topic,userID):
    '''
    kafka producer MemberSelect
    topic:選擇Topic
    userID:sql select * from member where userID = userID
    return: print('Message sending completed!')
    '''
    # 步驟1. 設定要連線到Kafka集群的相關設定

    props = {
        # Kafka集群在那裡?
        'bootstrap.servers': '192.168.1.81:9092',          # <-- 置換成要連接的Kafka集群
        'error_cb': error_cb                            # 設定接收error訊息的callback函數
    }
    # 步驟2. 產生一個Kafka的Producer的實例
    producer = Producer(props)
    # 步驟3. 指定想要發佈訊息的topic名稱

    topicList = ['members','recipe','fitness']

    topicName = topicList[topic]

    print(topicName)

    try:
        print('Start sending messages ...')
        host = '192.168.1.81'
        port = 3307
        user = 'root'
        passwd = 'iii'
        db = 'sport_db'
        charset = 'utf8mb4'
        conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset=charset)
        print('successfully connected')

        cursor = conn.cursor()


        sql ='''SELECT url from hiyd_V2 where  label = "{}" and strengh ="{}";'''.format(int(label),int(strengh))

        cursor.execute(sql)
        conn.commit()

        conn.close()

        data = cursor.fetchmany(1)

        data = str(data)

        print(data)

        producer.produce(topicName, value='{}'.format(data))
        producer.poll(0)  # <-- (重要) 呼叫poll來讓client程式去檢查內部的Buffer
        print('topic = {:s},value={:s}'.format(topicName,information))
        time.sleep(3)  # 讓主執行緒停個3秒

    except BufferError as e:
        # 錯誤處理
        sys.stderr.write('%% Local producer queue is full ({} messages awaiting delivery): try again\n'
                         .format(len(producer)))
    except Exception as e:
        print(e)
    # 步驟5. 確認所有在Buffer裡的訊息都己經送出去給Kafka了
    producer.flush(10)
    return print('Message sending completed!')

if __name__ == '__main__':
    memberSelect()