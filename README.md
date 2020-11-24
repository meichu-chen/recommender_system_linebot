# Recipe_Workout plans recommender
A health-based recipe and exercise plan recommendation system.
A Line chatbot that recommend recipes based on user's ingredient preference, daily calories consumption, recipes style preference 
and other users preference behavior. Users can also send a photo of gym equipment, the chatbot will tell you what the equipment is 
and provide a link to a website that teaches you how to exercise with that equipment.

## Database structure

All services and databases are built in docker containers, including python devops environment, mongoDB, MySQL and kafka. 

1. Raw data collected from the web --> store in mongoDB.
2. Push data to Hadoop file system that runs on local machines.
3. Utilize SparkSQL to preprocess our datas, and Spark Mllib for model training.
4. Use Tensorflow for image recognition model training.
5. Build a Line Chatbot App in python devops docker container, with pipenv for libraries version control.
6. Construct docker-compose.yml file to run all containers.
7. Connect all containers by port mapping.

![alt text](https://github.com/imkir0513/Recommender-system-linebot/blob/master/demo_image/structure.png)

## Line Chatbot API
1. Follow the chatbot.

![alt text](https://github.com/imkir0513/Recommender-system-linebot/blob/master/demo_image/follow_event.jpg)

2. Recipe recommendation.

![alt text](https://github.com/imkir0513/Recommender-system-linebot/blob/master/demo_image/recipe_recom.jpg)

3. Gym Equipment image recognition.

![alt text](https://github.com/imkir0513/Recommender-system-linebot/blob/master/demo_image/image_recog.jpg)

4. Functions as Saving workout plans or Saving recipes are also included. More demo images, please refer to demo_img directory.

