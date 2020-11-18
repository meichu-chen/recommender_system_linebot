FROM python:3.8.2
#設定一個工作目錄 /app
WORKDIR /app
# 複製當前目錄的全部資料進去 Container 的 /app
COPY . /app


# 安裝程式藥用的套件
RUN pip install pipenv
RUN apt-get update && apt-get install -y --no-install-recommends gcc
RUN apt-get install -y nano
RUN apt-get install 'ffmpeg'\
    'libsm6'\
    'libxext6' -y
#RUN pipenv update
RUN pipenv install --system --deploy

# 預計flask 要開啟 5000 port號 映射
EXPOSE 5000

# 執行命令句 - 叫container 預設執行 app.py
#CMD ["python", "app_2_revise3.py"]
#CMD ["python", "kafkaCmember.py"]
