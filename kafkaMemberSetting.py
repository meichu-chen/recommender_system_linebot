from confluent_kafka import Producer
import sys
import time
import random
# 用來接收從Consumer instance發出的error訊息
def error_cb(err):
    print('Error: %s' % err)

# 主程式進入點
def memberSetting(topic,information):
    '''
    kafka producer
    topic:選擇Topic
    information:要匯入的資料
    return: print('Message sending completed!')
    '''
    # 步驟1. 設定要連線到Kafka集群的相關設定

    props = {
        # Kafka集群在那裡?
        'bootstrap.servers': 'kafka:29092',          # <-- 置換成要連接的Kafka集群
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

        producer.produce(topicName, value='{}'.format(information))
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
    memberSetting()
