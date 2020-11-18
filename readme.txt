啟動方法

1. 找到docker-compose.yml，修改line access token & line access channel
 aws的金鑰刪除
 以及 ngrok auth,  ngrok username, ngrok password

2. docker-compose up -d

3. docker exec -it <container名字> bash

4. 修改line_secret_key裡面的line webhook URL

5. 手動 pip install cryptography, pip install flask_bootstrap

6. 執行 python kafkaCmember.py

7. 執行 python app_2_revise5.py

8.table_sql 為mysql table簡易查詢 建立table 刪除table 的sql語法