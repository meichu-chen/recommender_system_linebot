-- 看table資料
SELECT * from diary;
SELECT * from members;
SELECT * from plan_favorite;
SELECT * from recipe_favorite;
SELECT * from recommend_recipe;
SELECT * from workout_plans;
SELECT * FROM sport;


-- 看table設定
DESC diary;
DESC members;
DESC plan_favorite;
DESC recipe_favorite;
DESC recommend_recipe;
DESC workout_plans;
DESC sport;


-- 創造members表格
CREATE TABLE members ( 
userID				VARCHAR(45)		NOT NULL,
joindate 			TIMESTAMP		NOT NULL,
name				VARCHAR(100)	NOT NULL,
email				VARCHAR(100)	NULL,
age					INT				NULL,
gender				INT				NULL,
height				FLOAT			NULL,
weight				FLOAT			NULL,
activity_level		INT				NULL,
like_ingredient		VARCHAR(150)	NULL,
dislike_ingredient	VARCHAR(150)	NULL,
bmr					FLOAT			NULL,
tdee				FLOAT			null,
PRIMARY KEY (userID));

-- 刪除members表格
DROP tables members;

-- 創造recipe_favorite表格
CREATE TABLE recipe_favorite ( 
userID		VARCHAR(45)		NOT NULL ,
title 		VARCHAR(200) 	NOT NULL ,
url			VARCHAR(200)	NOT NULL,
add_time	TIMESTAMP	NOT NULL ,
insertID 	INT			NOT NULL AUTO_INCREMENT unique,
PRIMARY KEY (userID, url));

-- 刪除recipe_favorite表格
DROP tables recipe_favorite;

-- 創造plan_favorite表格
CREATE TABLE plan_favorite( 
userID		VARCHAR(45)		NOT NULL ,
title 		VARCHAR(200) 	NOT NULL ,
url			VARCHAR(200)	NOT NULL,
add_time	TIMESTAMP	NOT NULL ,
insertID 	INT			NOT NULL AUTO_INCREMENT unique,
PRIMARY KEY (userID, url));

-- 刪除plan_favorite表格
DROP tables plan_favorite;

-- 創造recommend_recipe表格
CREATE TABLE recommend_recipe ( 
userID		VARCHAR(40)		NOT NULL ,
url 		VARCHAR(200),
img_url		VARCHAR(400),
title		VARCHAR(100),
priority 	INT		NOT NULL AUTO_INCREMENT,
PRIMARY KEY (priority));

-- 刪除recommend_recipe表格
DROP TABLES recommend_recipe;

-- 創造sport表格
CREATE TABLE sport ( 
userID		VARCHAR(40)		NOT NULL ,
sport_id 	int				PRIMARY KEY AUTO_INCREMENT,
sport_name	VARCHAR(40),
sport_time	int,
join_date 	TIMESTAMP		NOT NULL);

-- 刪除sporte表格
DROP TABLE sport;

-- 創造diary表格
CREATE TABLE diary ( 
userID		VARCHAR(40)		NOT NULL ,
diary_id 	int				PRIMARY KEY AUTO_INCREMENT,
food_name	VARCHAR(40),
food_calory	int,
join_date 	TIMESTAMP		NOT NULL);

-- 刪除diary表格
DROP TABLE diary;

SELECT * FROM recipe_favorite WHERE userID = '{}' ORDER BY add_time DESC;

SELECT m.userID, m.name, d.food_name, d.food_calory, d.join_date
FROM members m JOIN diary d
WHERE m.userID = d.userID
ORDER BY d.join_date DESC;


CREATE TABLE activity_level ( 
activity_levelno	INT(1)			NOT NULL,
activity_level	 	VARCHAR(10)		NOT NULL);

DROP TABLES activity_level;

CREATE TABLE gender ( 
genderno			INT(1)		NOT NULL,
gender	 			VARCHAR(1)		NOT NULL);


INSERT INTO activity_level(activity_levelno, activity_level)
VALUE (1, '久坐(沒什麼運動)');

INSERT INTO activity_level(activity_levelno, activity_level)
VALUE (2, '輕量活動(輕鬆運動3-5天)');

INSERT INTO activity_level(activity_levelno, activity_level)
VALUE (3, '中度活動量(中等強度運動3-5天)');

INSERT INTO activity_level(activity_levelno, activity_level)
VALUE (4, '高度活動量(高強度運動6-7天)');

INSERT INTO activity_level(activity_levelno, activity_level)
VALUE (5, '非常高度活動量(勞力密集工作或一天訓練兩次以上)');


INSERT INTO gender(genderno, gender)
VALUE (1, '男');

INSERT INTO gender(genderno, gender)
VALUE (2, '女');

