
'''
整體功能描述
'''
'''

Application 主架構

'''
# import recipe_recommender
import recipe_recommend.find_recipe_user_preference as rfp
# import image_recognition function and model
from image_recognition.check_v3_model import photoIdentification



# 引用Web Server套件
from flask import Flask, request, abort, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import pymysql, time
#from flask_mysqldb import MySQL
from flask_bootstrap import Bootstrap
# 從linebot 套件包裡引用 LineBotApi 與 WebhookHandler 類別
from linebot import (
    LineBotApi, WebhookHandler
)
# 引用無效簽章錯誤
from linebot.exceptions import (
    InvalidSignatureError
)
# 載入json處理套件
import json




# 載入基礎設定檔
secretFileContentJson=json.load(open("./line_secret_key",'r',encoding='utf8'))
server_url=secretFileContentJson.get("server_url")

# 設定Server啟用細節
app = Flask(__name__,static_url_path = "/static" , static_folder = "./static/")

# 生成實體物件
line_bot_api = LineBotApi(secretFileContentJson.get("channel_access_token"))
handler = WebhookHandler(secretFileContentJson.get("secret_key"))

# 啟動server對外接口，使Line能丟消息進來
@app.route("/", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# pymysql設定資料庫連線設定
host = 'mysql'
port = 3306
user = 'root'
passwd = 'iii'
db = 'capstone'

# SQLAlchemy設定資料庫連線設定
class Config(object):
    '''配置參數'''
    #　sqlalchemy的配置參數
    SQLALCHEMY_DATABASE_URI = "mysql://root:root@mysql:3306/capstone"
    #　設置是否sqlalchemy自動追蹤資料庫的修改並發送訊號
    SQLALCHEMY_TRACK_MODIFICATIONS = False

app.config.from_object(Config)

# 創建資料庫sqlalchemy工具對象
db2 = SQLAlchemy(app)


'''

消息判斷器
讀取指定的json檔案後，把json解析成不同格式的SendMessage
讀取檔案，
把內容轉換成json
將json轉換成消息
放回array中，並把array傳出。

'''

# 引用會用到的套件
from linebot.models import (
    ImagemapSendMessage, TextSendMessage, ImageSendMessage, LocationSendMessage, FlexSendMessage, VideoSendMessage
, PostbackTemplateAction, MessageTemplateAction, URITemplateAction, QuickReply, QuickReplyButton, URIAction, BubbleContainer,
ImageComponent, BoxComponent, SpacerComponent, ButtonComponent, SeparatorComponent, TextComponent
)

from linebot.models.template import (
    ButtonsTemplate, CarouselTemplate, ConfirmTemplate, ImageCarouselTemplate,

)
import tdee_function as tdee
import math
from linebot.models import (PostbackEvent)
from urllib.parse import parse_qs
from kafkaMemberSetting import memberSetting
from kafkaMemberSelect import memberSelect


from linebot.models.template import *


def detect_json_array_to_new_message_array(fileName):
    # 開啟檔案，轉成json
    with open(fileName, 'r', encoding='utf-8') as f:
        jsonArray = json.load(f)

    # 解析json
    returnArray = []
    for jsonObject in jsonArray:

        # 讀取其用來判斷的元件
        message_type = jsonObject.get('type')

        # 轉換
        if message_type == 'text':
            returnArray.append(TextSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'imagemap':
            returnArray.append(ImagemapSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'template':
            returnArray.append(TemplateSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'image':
            returnArray.append(ImageSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'sticker':
            returnArray.append(StickerSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'audio':
            returnArray.append(AudioSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'location':
            returnArray.append(LocationSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'flex':
            returnArray.append(FlexSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'video':
            returnArray.append(FlexSendMessage.new_from_json_dict(jsonObject))

            # 回傳
    return returnArray


'''

handler處理關注消息
用戶關注時，讀取 素材 -> 關注 -> reply.json
將其轉換成可寄發的消息，傳回給Line

'''

# 引用套件
from linebot.models import (
    FollowEvent
)


# 關注事件處理
@handler.add(FollowEvent)
def process_follow_event(event):
    # 讀取並轉換
    result_message_array = []
    replyJsonPath = "素材/關注/reply.json"
    result_message_array = detect_json_array_to_new_message_array(replyJsonPath)

    # 消息發送
    line_bot_api.reply_message(
        event.reply_token,
        result_message_array
    )

    # 啟動第一張圖文選單
    linkRichMenuId = open("素材/" + 'rich_menu_0' + '/rich_menu_id', 'r').read()
    line_bot_api.link_rich_menu_to_user(event.source.user_id, linkRichMenuId)

    replyJsonPath = '素材/' + 'rich_menu_0' + "/reply.json"
    result_message_array = detect_json_array_to_new_message_array(replyJsonPath)


'''

handler處理文字消息
收到用戶回應的文字消息，
按文字消息內容，往素材資料夾中，找尋以該內容命名的資料夾，讀取裡面的reply.json
轉譯json後，將消息回傳給用戶

'''

# 引用套件
from linebot.models import (
    MessageEvent, TextMessage
)

# 文字消息處理
@handler.add(MessageEvent,message=TextMessage)
def process_text_message(event):



    if event.message.text == '找食譜':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='請以"食材"開頭後，輸入您要找的食材（單詞以空白隔開)')
        )

    elif '食材' in event.message.text:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='你輸入的食材有：{}'.format(event.message.text[3:]))
        )



    elif event.message.text == '食譜推薦中...':
        pass

    else:


        # 讀取本地檔案，並轉譯成消息
        result_message_array =[]
        replyJsonPath = "素材/"+event.message.text+"/reply.json"
        result_message_array = detect_json_array_to_new_message_array(replyJsonPath)

        # 發送
        line_bot_api.reply_message(
            event.reply_token,
            result_message_array
        )


'''

handler處理Postback Event

載入功能選單與啟動特殊功能

解析postback的data，並按照data欄位判斷處理

現有三個欄位
menu, folder, tag

若folder欄位有值，則
    讀取其reply.json，轉譯成消息，並發送

若menu欄位有值，則
    讀取其rich_menu_id，並取得用戶id，將用戶與選單綁定
    讀取其reply.json，轉譯成消息，並發送

'''


@handler.add(PostbackEvent)
def process_postback_event(event):
    query_string_dict = parse_qs(event.postback.data)

    print(query_string_dict)
    if 'folder' in query_string_dict:

        result_message_array = []

        replyJsonPath = '素材/' + query_string_dict.get('folder')[0] + "/reply.json"
        result_message_array = detect_json_array_to_new_message_array(replyJsonPath)

        line_bot_api.reply_message(
            event.reply_token,
            result_message_array
        )
    elif 'menu' in query_string_dict:

        linkRichMenuId = open("素材/" + query_string_dict.get('menu')[0] + '/rich_menu_id', 'r').read()
        line_bot_api.link_rich_menu_to_user(event.source.user_id, linkRichMenuId)

        replyJsonPath = '素材/' + query_string_dict.get('menu')[0] + "/reply.json"
        result_message_array = detect_json_array_to_new_message_array(replyJsonPath)

        line_bot_api.reply_message(
            event.reply_token,
            result_message_array
        )

    # '''取出用戶Line的userID及username並存到資料庫'''

    elif 'menu2' in query_string_dict:
        # 建立連線
        conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset='utf8')
        # 建立游標
        cursor = conn.cursor()

        linkRichMenuId = open("素材/" + query_string_dict.get('menu2')[0] + '/rich_menu_id', 'r').read()
        line_bot_api.link_rich_menu_to_user(event.source.user_id, linkRichMenuId)

        # 取出消息內User的資料
        user_profile = line_bot_api.get_profile(event.source.user_id)
        userID = str(user_profile.user_id)

        # 將用戶資訊存在檔案內
        with open("./users.txt", "a") as myfile:
            myfile.write(json.dumps(vars(user_profile), sort_keys=True))
            myfile.write('\n')

        joindate = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        #time.localtime()
        informationI = 'INSER,{:s},{:s},{:s}'.format(str(userID), str(user_profile.display_name), str(joindate))

        try:
            # kafkaP(topic,information)
            # topicList = ['members','recipe','fitness']

            memberSetting(0,informationI)

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="%s您好！\n歡迎加入【食健主義】\n\n在開始使用之前，請點選下方選單\n --→「我的基本資料」\n回答幾個問題，讓我們更了解你的喜好ღ" % (user_profile.display_name)))

        except pymysql.err.IntegrityError:
            print('Error', user_profile.user_id, 'existed.')
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="親愛的 %s 您好！\n感謝您回來繼續使用【食健主義】ღ" % (user_profile.display_name)))

        # 關閉游標及連線
        cursor.close()
        conn.close()

    elif 'information' in query_string_dict:

        conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset='utf8')
        cursor = conn.cursor()

        # line_bot_api.reply_message(event.reply_token, TextSendMessage(text="come on"))

        # 取出消息內User的資料
        user_profile = line_bot_api.get_profile(event.source.user_id)
        userID = str(user_profile.user_id)

        try:
            @app.route('/register1/<userID>', methods=['GET'])
            def register1(userID):
                conn = pymysql.connect(host='mysql', port=3306, user='root', password='iii', db='capstone', charset='utf8')
                cur = conn.cursor()

                sql = '''SELECT name,email,gender,age,height,weight,activity_level,like_ingredient,dislike_ingredient from members where userID = "{}";'''.format(userID)

                cur.execute(sql)

                u = cur.fetchall()

                conn.close()

                return render_template('register1.html' ,u = u, ID = userID)

            @app.route('/submit', methods=['POST'])
            def submit():
                user_ID = request.values.get('user_ID')
                name = str(request.values.get('name'))
                email = str(request.values.get('email'))
                gender = int(request.form.get('gender'))
                age = int(request.form.get('age'))
                height = float(request.form.get('height'))
                weight = float(request.form.get('weight'))
                activity_level = int(request.form.get('activity_level'))
                like_ingredient = str(request.form.get('like_ingredient'))
                dislike_ingredient = str(request.form.get('dislike_ingredient'))
                ans1, ans2 = tdee.tdee_calculator(gender, age, height, weight, activity_level)

                informationU = "UPDATE,{},{},{},{},{},{},{},{},{},{},{},{}".format(name, email, gender, age, height, weight, activity_level,like_ingredient, dislike_ingredient,ans1,ans2, user_ID)

                memberSetting(0,informationU)

                # sql = '''UPDATE members
                #         SET name = '{}', email = '{}', gender = '{}', age = '{}', height = '{}', weight = '{}', activity_level = '{}', like_ingredient = '{}', dislike_ingredient = '{}', bmr = '{}',tdee = '{}'
                #         WHERE userID = {};'''.format(name, email, gender, age, height, weight,activity_level, like_ingredient,dislike_ingredient, ans1, ans2user_ID)

         # ================  這一區塊把食譜推薦跑模型的時機放在使用者填完個人資料表單之後 ===============================================
                recommend_result = rfp.main(like_ingredient.split())
                conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db)
                cursor = conn.cursor()

                sql = '''INSERT INTO recommend_recipe (userID, url, img_url, title)
                            VALUES  ("{}", "{}", "{}", "{}"), ("{}", "{}", "{}", "{}"), ("{}", "{}", "{}", "{}"),
                                    ("{}", "{}", "{}", "{}"), ("{}", "{}", "{}", "{}"), ("{}", "{}", "{}", "{}"),
                                    ("{}", "{}", "{}", "{}"), ("{}", "{}", "{}", "{}"), ("{}", "{}", "{}", "{}"),
                                    ("{}", "{}", "{}", "{}"), ("{}", "{}", "{}", "{}"), ("{}", "{}", "{}", "{}"),
                                    ("{}", "{}", "{}", "{}"), ("{}", "{}", "{}", "{}"), ("{}", "{}", "{}", "{}"),
                                    ("{}", "{}", "{}", "{}"), ("{}", "{}", "{}", "{}"), ("{}", "{}", "{}", "{}"),
                                    ("{}", "{}", "{}", "{}"), ("{}", "{}", "{}", "{}");
                                    '''.format(user_ID, recommend_result[0][1][1], recommend_result[0][1][2],recommend_result[0][0],
                                               user_ID, recommend_result[1][1][1], recommend_result[1][1][2],recommend_result[1][0],
                                               user_ID, recommend_result[2][1][1], recommend_result[2][1][2],recommend_result[2][0],
                                               user_ID, recommend_result[3][1][1], recommend_result[3][1][2],recommend_result[3][0],
                                               user_ID, recommend_result[4][1][1], recommend_result[4][1][2],recommend_result[4][0],
                                               user_ID, recommend_result[5][1][1], recommend_result[5][1][2],recommend_result[5][0],
                                               user_ID, recommend_result[6][1][1], recommend_result[6][1][2],recommend_result[6][0],
                                               user_ID, recommend_result[7][1][1], recommend_result[7][1][2],recommend_result[7][0],
                                               user_ID, recommend_result[8][1][1], recommend_result[8][1][2],recommend_result[8][0],
                                               user_ID, recommend_result[9][1][1], recommend_result[9][1][2],recommend_result[9][0],
                                               user_ID, recommend_result[10][1][1], recommend_result[10][1][2],recommend_result[10][0],
                                               user_ID, recommend_result[11][1][1], recommend_result[11][1][2],recommend_result[11][0],
                                               user_ID, recommend_result[12][1][1], recommend_result[12][1][2],recommend_result[12][0],
                                               user_ID, recommend_result[13][1][1], recommend_result[13][1][2],recommend_result[13][0],
                                               user_ID, recommend_result[14][1][1], recommend_result[14][1][2],recommend_result[14][0],
                                               user_ID, recommend_result[15][1][1], recommend_result[15][1][2],recommend_result[15][0],
                                               user_ID, recommend_result[16][1][1], recommend_result[16][1][2],recommend_result[16][0],
                                               user_ID, recommend_result[17][1][1], recommend_result[17][1][2],recommend_result[17][0],
                                               user_ID, recommend_result[18][1][1], recommend_result[18][1][2],recommend_result[18][0],
                                               user_ID, recommend_result[19][1][1], recommend_result[19][1][2],recommend_result[19][0],)
                cursor.execute(sql)
                conn.commit()
                cursor.close()
                conn.close()
        # =================================================================================================================================
                return render_template('sucess.html', content1=ans1, content2=ans2)
        except:
            pass

        sql = '''SELECT name,email,gender,age,height,weight,activity_level,like_ingredient,dislike_ingredient,bmr,tdee
                from members where userID = "{}";'''.format(userID)

        cursor.execute(sql)

        data = cursor.fetchmany(1)
        data0 = '姓名: ' + str(data[0][0]) + '\n'
        data1 = 'Email: ' + str(data[0][1]) + '\n'
        data2 = str(data[0][2])
        if data2 == '1':
            data2 = '男'
        elif data2 == '2':
            data2 = '女'
        data2 = '性別: ' + data2 + '\n'
        data3 = '年齡: ' + str(data[0][3]) + '\n'
        data4 = '身高: ' + str(data[0][4]) + '\n'
        data5 = '體重: ' + str(data[0][5]) + '\n'
        data6 = str(data[0][6])
        if data6 == '1':
            data6 = '久坐(沒什麼運動)'
        elif data6 == '2':
            data6 = '輕量活動(輕鬆運動3-5天)'
        elif data6 == '3':
            data6 = '中度活動量(中等強度運動3-5天)'
        elif data6 == '4':
            data6 = '高度活動量(高強度運動6-7天)'
        elif data6 == '5':
            data6 = '非常高度活動量(勞力密集工作或一天訓練兩次以上)'
        data6 = '平常活動頻率: ' + data6 + '\n'
        data7 = '喜歡的食材: ' + str(data[0][7]) + '\n'
        data8 = '討厭或過敏的食材: ' + str(data[0][8]) + '\n'
        data9 = 'bmr: ' + str(data[0][9]) + '\n'
        data10 = 'tdee: ' + str(data[0][10])

        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(
                alt_text='FlexMessage',
                direction="ltr",
                contents=BubbleContainer(
                    header=BoxComponent(
                        layout='baseline',
                        contents=[TextComponent(text='我的基本資料', align='center', decoration='underline', weight='bold')]),
                    body=BoxComponent(
                        layout='vertical',
                        contents=[
                            TextComponent(text=' 1. {}'.format(data0)),
                            TextComponent(text=' 2. {}'.format(data1)),
                            TextComponent(text=' 3. {}'.format(data2)),
                            TextComponent(text=' 4. {}'.format(data3)),
                            TextComponent(text=' 5. {}'.format(data4)),
                            TextComponent(text=' 6. {}'.format(data5)),
                            TextComponent(text=' 7. {}'.format(data6)),
                            TextComponent(text=' 8. {}'.format(data7)),
                            TextComponent(text=' 9. {}'.format(data8)),
                            TextComponent(text='10. {}'.format(data9)),
                            TextComponent(text='11. {}'.format(data10))]),
                    footer=BoxComponent(
                        layout='vertical',
                        spacing='sm',
                        contents=[
                            # callAction, separator, websiteAction
                            SpacerComponent(size='sm'),
                            # callAction
                            ButtonComponent(
                                style='link',
                                height='sm',
                                action=URIAction(label='更改基本資料',
                                                 uri='{}'.format(server_url) + '/register1/' + '{}'.format(userID))
                                # separator

                            )])
                )
            )
        )

        cursor.close()
        conn.close()

### ======== 以下整串都是跟運動課表連續對話有關 ============================================
    elif 'exercise' in query_string_dict:
        line_bot_api.reply_message(  # 回復傳入的訊息文字
            event.reply_token,
            TextSendMessage(
        ########################################################
                text='請選擇訓練部位',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=PostbackTemplateAction(
                                label='手臂',
                                text='手臂',
                                data='m&tricep'
                            )
                        ),
                        QuickReplyButton(
                            action=PostbackTemplateAction(
                                label='胸',
                                text='胸',
                                data='m&chest'
                            )
                        ),
                        QuickReplyButton(
                            action=PostbackTemplateAction(
                                label='背',
                                text='背',
                                data='m&back'
                            )
                        ),
                        QuickReplyButton(
                            action=PostbackTemplateAction(
                                label='腿',
                                text='腿',
                                data='m&leg'
                            )
                        ),
                        QuickReplyButton(
                            action=PostbackTemplateAction(
                                label='肩',
                                text='肩',
                                data='m&shoulder'
                            )
                        ),
                        QuickReplyButton(
                            action=PostbackTemplateAction(
                                label='腹肌',
                                text='腹肌',
                                data='m&ab'
                            )
                        )
                    ]
                )
            )
        )
    elif event.postback.data[0:1] == "m":  # 如果回傳值為「選擇運動部位」
        muscle = event.postback.data[2:]
        line_bot_api.reply_message(  # 回復傳入的訊息文字
            event.reply_token,
            TextSendMessage(
                ########################################################
                text='請選擇訓練頻次',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=PostbackTemplateAction(
                                label='一週三次',
                                text='一週三次',
                                data='f&'+muscle+'&3' + '&0'
                            )
                        ),
                        QuickReplyButton(
                            action=PostbackTemplateAction(
                                label='一週四次',
                                text='一週四次',
                                data='f&'+muscle+'&4' + '&0'
                            )
                        ),
                        QuickReplyButton(
                            action=PostbackTemplateAction(
                                label='一週五次',
                                text='一週五次',
                                data='f&'+muscle+'&5' + '&0'
                            )
                        )
                    ]
                )
            )
        )

    # elif event.postback.data[0:1] == "i":  # 如果回傳值為「選擇運動強度」
    #     muscle_intensity = event.postback.data[2:]  # 透過切割字串取得部位及強度文字
    #     line_bot_api.reply_message(  # 回復傳入的訊息文字
    #         event.reply_token,
    #         TextSendMessage(
    #             ########################################################
    #             text='請選擇訓練頻次',
    #             quick_reply=QuickReply(
    #                 items=[
    #                     QuickReplyButton(
    #                         action=PostbackTemplateAction(
    #                             label='一週三次',
    #                             text='一週三次',
    #                             data='f&' + muscle_intensity + '&3'
    #                         )
    #                     ),
    #                     QuickReplyButton(
    #                         action=PostbackTemplateAction(
    #                             label='一週四次',
    #                             text='一週四次',
    #                             data='f&' + muscle_intensity + '&4'
    #                         )
    #                     ),
    #                     QuickReplyButton(
    #                         action=PostbackTemplateAction(
    #                             label='一週五次',
    #                             text='一週五次',
    #                             data='f&' + muscle_intensity + '&5' + '&0'
    #                         )
    #                     )
    #                 ]
    #             )
    #         )
    #     )

    elif event.postback.data[0:1] == "f":  # 如果回傳值為"f"

        searching_word = event.postback.data[2:]  # 透過切割字串取得使用者輸入所有文字
        # ===== 以下要去資料庫做搜尋的動作 ==============================================
        muscle = searching_word.split('&')[0]
        frequency = searching_word.split('&')[1]
        page_lasttime = int(searching_word.split('&')[2])
        page_thistime = page_lasttime + 2

        conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset='utf8')
        cursor = conn.cursor()
        # 取出消息內User的資料
        # user_profile = line_bot_api.get_profile(event.source.user_id)
        # userID = str(user_profile.user_id)
        sql = '''SELECT url, img_url, title
        from workout_plans
        where target = "{}" AND frequency = "{}" LIMIT {};'''.format(str(muscle), str(frequency), page_thistime)
        cursor.execute(sql)
        data = cursor.fetchall()
        # line_bot_api.reply_message(
        #     event.reply_token,
        #     TextSendMessage(text="您輸入的內容為：{}".format(str(data[0][2]))))
        if len(data) < page_thistime:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='推薦給您的運動課表已讀取完最後一筆，若要搜尋更多可直接點選連結到該網站搜尋')
            )

        else:
# ==========================================================================================
            line_bot_api.reply_message(
                event.reply_token,
                TemplateSendMessage(
                    alt_text='Carousel template',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                thumbnail_image_url='{}'.format(str(data[-1][1])),
                                title='{}'.format(str(data[-1][2])[:40]),
                                text='{}相關運動'.format(muscle),
                                actions=[
                                    URITemplateAction(
                                        label='前往課表網頁',
                                        uri='{}'.format(str(data[-1][0]))
                                    ),
                                    PostbackTemplateAction(
                                        label='加入我的最愛',
                                        data='saveplan={}&{}'.format(str(data[-1][2]),str(data[-1][0]))
                                    )
                                ]
                            ),
                            CarouselColumn(
                                thumbnail_image_url='{}'.format(str(data[-2][1])),
                                title='{}'.format(str(data[-2][2])[:40]),
                                text='{}相關運動'.format(muscle),
                                actions=[
                                    URITemplateAction(
                                        label='前往課表網頁',
                                        uri='{}'.format(str(data[-2][0]))
                                    ),
                                    PostbackTemplateAction(
                                        label='加入我的最愛',
                                        data='saveplan={}&{}'.format(str(data[-2][2]),str(data[-2][0]))
                                    )

                                ]
                            ),
                            CarouselColumn(
                                thumbnail_image_url='https://www.iislands.com/image/images/img0006.png',
                                title='More',
                                text='更多',
                                actions=[
                                    URITemplateAction(
                                        label='直接前往該網站搜尋',
                                        uri='https://www.muscleandstrength.com/workout-routines'
                                    ),
                                    PostbackTemplateAction(
                                        label='看更多我推薦的課表',
                                        data='f&{}&{}&{}'.format(muscle, frequency, page_thistime)
                                    )

                                ]
                            )

                        ]
                    )
                )
            )

        cursor.close()
        conn.close()
        ################################################################################################################

# #===================================================================================

# =========== 以下區間為食譜推薦 ======================================================
    elif 'recipe' in query_string_dict:  # 如果回傳值為「recipe」

        #====== 下SQL指令去抓預先推薦好的資料 ===============
        conn = pymysql.connect(host = host, port = port, user = user, passwd = passwd, db = db, charset = 'utf8')
        cursor = conn.cursor()
        # 取出消息內User的資料
        user_profile = line_bot_api.get_profile(event.source.user_id)
        userID = str(user_profile.user_id)

        sql = '''SELECT url, img_url, title
        from recommend_recipe
        where userID = "{}"
        ORDER BY priority
        DESC LIMIT 5;'''.format(userID)
        cursor.execute(sql)
        data = cursor.fetchall()
        #prefered_ingred = (data[0][0]).split()
        cursor.close()
        conn.close()

        #recommend_result = rfp.main(prefered_ingred)


        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                alt_text='Carousel template',
                template=CarouselTemplate(
                    columns=[
                        CarouselColumn(
                            thumbnail_image_url='{}'.format(str(data[0][1])),
                            title='{}'.format(str(data[0][2])),
                            text='選我選我',
                            actions=[
                                URITemplateAction(
                                    label='前往食譜網頁',
                                    uri='{}'.format(str(data[0][0]))
                                ),
                                PostbackTemplateAction(
                                    label='加入我的最愛',
                                    data='saverecipe={}&{}'.format(str(data[0][2]),str(data[0][0]))
                                ),

                            ]
                        ),
                        CarouselColumn(
                            thumbnail_image_url='{}'.format(str(data[1][1])),
                            title='{}'.format(str(data[1][2])),
                            text='選我選我',
                            actions=[
                                URITemplateAction(
                                    label='前往食譜網頁',
                                    uri='{}'.format(str(data[1][0]))
                                ),
                                PostbackTemplateAction(
                                    label='加入我的最愛',
                                    data='saverecipe={}&{}'.format(str(data[1][2]), str(data[1][0]))
                                ),

                            ]
                        ),
                        CarouselColumn(
                            thumbnail_image_url='{}'.format(str(data[2][1])),
                            title='{}'.format(str(data[2][2])),
                            text='選我選我',
                            actions=[
                                URITemplateAction(
                                    label='前往食譜網頁',
                                    uri='{}'.format(str(data[2][0]))
                                ),
                                PostbackTemplateAction(
                                    label='加入我的最愛',
                                    data='saverecipe={}&{}'.format(str(data[2][2]), str(data[2][0]))
                                ),

                            ]
                        ),
                        CarouselColumn(
                            thumbnail_image_url='{}'.format(str(data[3][1])),
                            title='{}'.format(str(data[3][2])),
                            text='選我選我',
                            actions=[
                                URITemplateAction(
                                    label='前往食譜網頁',
                                    uri='{}'.format(str(data[3][0]))
                                ),
                                PostbackTemplateAction(
                                    label='加入我的最愛',
                                    data='saverecipe={}&{}'.format(str(data[3][2]), str(data[3][0]))
                                ),

                            ]
                        ),
                        CarouselColumn(
                            thumbnail_image_url='{}'.format(str(data[4][1])),
                            title='{}'.format(str(data[4][2])),
                            text='選我選我',
                            actions=[
                                URITemplateAction(
                                    label='前往食譜網頁',
                                    uri='{}'.format(str(data[4][0]))
                                ),
                                PostbackTemplateAction(
                                    label='加入我的最愛',
                                    data='saverecipe={}&{}'.format(str(data[4][2]), str(data[4][0]))
                                ),

                            ]
                        ),
                        CarouselColumn(
                            thumbnail_image_url='https://www.iislands.com/image/images/img0006.png',
                            title='More',
                            text='更多',
                            actions=[
                                URITemplateAction(
                                    label='直接前往該網站搜尋',
                                    uri='https://icook.tw/'
                                ),
                                PostbackTemplateAction(
                                    label='看更多我推薦的食譜',
                                    data='getrecipe={}&{}'.format(userID,5)
                                )

                            ]
                        )
                    ]
                )
            )
        )
# =============== 嘗試看更多菜單 ====================================================
    elif event.postback.data.split('=')[0] == "getrecipe":  # 如果回傳值為「morerecipe」
        page_lasttime = int(event.postback.data.split('&')[1])
        page_thistime = page_lasttime + 5
        user_profile = line_bot_api.get_profile(event.source.user_id)
        userID = str(user_profile.user_id)

        # ====== 下SQL指令去抓預先推薦好的資料 ===============
        conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset='utf8')
        cursor = conn.cursor()
        sql = '''SELECT url, img_url, title
                from recommend_recipe
                where userID = "{}"
                ORDER BY priority
                DESC LIMIT {};'''.format(userID, page_thistime)
        cursor.execute(sql)
        data = cursor.fetchall()
        # prefered_ingred = (data[0][0]).split()
        cursor.close()
        conn.close()



        if len(data) < page_thistime:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='推薦給您的菜單資料已讀取完最後一筆，若要搜尋更多可透過修改個人資料表內喜好食材欄位，或直接輸入關鍵字“找食譜”')
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TemplateSendMessage(
                    alt_text='Carousel template',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                thumbnail_image_url='{}'.format(str(data[-5][1])),
                                title='{}'.format(str(data[-5][2])),
                                text='選我選我',
                                actions=[
                                    URITemplateAction(
                                        label='前往食譜網頁',
                                        uri='{}'.format(str(data[-5][0]))
                                    ),
                                    PostbackTemplateAction(
                                        label='加入我的最愛',
                                        data='saverecipe={}&{}'.format(str(data[-5][2]), str(data[-5][0]))
                                    ),

                                ]
                            ),
                            CarouselColumn(
                                thumbnail_image_url='{}'.format(str(data[-4][1])),
                                title='{}'.format(str(data[-4][2])),
                                text='選我選我',
                                actions=[
                                    URITemplateAction(
                                        label='前往食譜網頁',
                                        uri='{}'.format(str(data[-4][0]))
                                    ),
                                    PostbackTemplateAction(
                                        label='加入我的最愛',
                                        data='saverecipe={}&{}'.format(str(data[-4][2]), str(data[-4][0]))
                                    ),

                                ]
                            ),
                            CarouselColumn(
                                thumbnail_image_url='{}'.format(str(data[-3][1])),
                                title='{}'.format(str(data[-3][2])),
                                text='選我選我',
                                actions=[
                                    URITemplateAction(
                                        label='前往食譜網頁',
                                        uri='{}'.format(str(data[-3][0]))
                                    ),
                                    PostbackTemplateAction(
                                        label='加入我的最愛',
                                        data='saverecipe={}&{}'.format(str(data[-3][2]), str(data[-3][0]))
                                    ),

                                ]
                            ),
                            CarouselColumn(
                                thumbnail_image_url='{}'.format(str(data[-2][1])),
                                title='{}'.format(str(data[-2][2])),
                                text='選我選我',
                                actions=[
                                    URITemplateAction(
                                        label='前往食譜網頁',
                                        uri='{}'.format(str(data[-2][0]))
                                    ),
                                    PostbackTemplateAction(
                                        label='加入我的最愛',
                                        data='saverecipe={}&{}'.format(str(data[-2][2]), str(data[-2][0]))
                                    ),

                                ]
                            ),
                            CarouselColumn(
                                thumbnail_image_url='{}'.format(str(data[-1][1])),
                                title='{}'.format(str(data[-1][2])),
                                text='選我選我',
                                actions=[
                                    URITemplateAction(
                                        label='前往食譜網頁',
                                        uri='{}'.format(str(data[-1][0]))
                                    ),
                                    PostbackTemplateAction(
                                        label='加入我的最愛',
                                        data='saverecipe={}&{}'.format(str(data[-1][2]), str(data[-1][0]))
                                    ),

                                ]
                            ),
                            CarouselColumn(
                                thumbnail_image_url='https://www.iislands.com/image/images/img0006.png',
                                title='More',
                                text='更多',
                                actions=[
                                    URITemplateAction(
                                        label='直接前往該網站搜尋',
                                        uri='https://icook.tw/'
                                    ),
                                    PostbackTemplateAction(
                                        label='看更多我推薦的食譜',
                                        data='getrecipe={}&{}'.format(userID, page_thistime)
                                    )

                                ]
                            )
                        ]
                    )
                )
            )



# =============== 以下為課表加入我的最愛區塊 =================================================
    elif event.postback.data.split('=')[0] == "saveplan":  # 如果回傳值為「saveplan」
        searching_word = event.postback.data.split('=')[1]  # 透過切割字串取得課表標題及網址
        title = searching_word.split('&')[0]
        url = searching_word.split('&')[1]

        user_profile = line_bot_api.get_profile(event.source.user_id)
        userID = str(user_profile.user_id)
        # ====== 跑食譜推薦的程式 ===============
        conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset='utf8')
        cursor = conn.cursor()
        addTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        sql = '''INSERT INTO plan_favorite (userID, title, url, add_time) VALUES("{}","{}","{}","{}");'''.format(userID, title, url, addTime)
        cursor.execute(sql)
        conn.commit()

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="已加入：{}".format(title)))



        cursor.close()
        conn.close()

# ========================================================================================

# =============== 以下為食譜加入我的最愛區塊 =================================================
    elif event.postback.data.split('=')[0] == "saverecipe":  # 如果回傳值為「saveplan」
        searching_word = event.postback.data.split('=')[1]  # 透過切割字串取得課表標題及網址
        title = searching_word.split('&')[0]
        url = searching_word.split('&')[1]
        # line_bot_api.reply_message(
        #     event.reply_token,
        #     TextSendMessage(text="您輸入的內容為：{}".format(url[:40])))
        user_profile = line_bot_api.get_profile(event.source.user_id)
        userID = str(user_profile.user_id)
        # ====== 跑食譜推薦的程式 ===============
        conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset='utf8')
        cursor = conn.cursor()
        addTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        sql = '''INSERT INTO recipe_favorite (userID, title, url, add_time) VALUES("{}","{}","{}","{}");'''.format(userID, title, url, addTime)
        cursor.execute(sql)
        conn.commit()

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="已加入：{}".format(title)))


        cursor.close()
        conn.close()

# ========= 使用者點選我的最愛動作 ===========================================================
    elif 'love' in query_string_dict:

        app.secret_key = 'many random bytes'

        #取出消息內User的資料
        user_profile = line_bot_api.get_profile(event.source.user_id)
        userID = str(user_profile.user_id)

        try:
            #食譜我的最愛查詢
            @app.route('/recipe_love/<userID>', methods=['GET'])
            def recipeCollect(userID):
                conn = pymysql.connect(host = host, port = port, user = user, passwd = passwd, db = db, charset = 'utf8')
                cur = conn.cursor()
                sql = """SELECT * FROM recipe_favorite WHERE userID='{}' ORDER BY add_time DESC;""".format(userID)
                cur.execute(sql)
                u = cur.fetchall()
                cur.close()
                conn.close()
                return render_template('recipe_love.html', recipe_favorite=u, userID=userID)

            #食譜我的最愛刪除
            @app.route('/delete', methods = ['POST','GET'])
            def delete():
                if request.method == 'POST':
                    userID = request.form['userID']
                    insertID = request.form['insertID']
                    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset='utf8')
                    flash("成功刪除！")
                    cur = conn.cursor()
                    sql = """DELETE FROM recipe_favorite WHERE insertID='{}';""".format(insertID)
                    cur.execute(sql)
                    conn.commit()
                    cur.close()
                    conn.close()
                    return redirect(url_for('recipeCollect', userID = userID))

            #健身課表我的最愛查詢
            @app.route('/plan_love/<userID>', methods=['GET'])
            def planCollect(userID):
                conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset='utf8')
                cur = conn.cursor()
                sql = """SELECT * FROM plan_favorite WHERE userID='{}' ORDER BY add_time DESC""".format(userID)
                cur.execute(sql)
                u = cur.fetchall()
                cur.close()
                conn.close()
                return render_template('plan_love.html', plan_favorite = u, userID = userID)

            #健身課表我的最愛刪除
            @app.route('/remove', methods = ['POST','GET'])
            def remove():
                if request.method == 'POST':
                    userID = request.form['userID']
                    insertID = request.form['insertID']
                    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset='utf8')
                    flash("成功刪除！")
                    cur = conn.cursor()
                    sql = """DELETE FROM plan_favorite WHERE insertID='{}';""".format(insertID)
                    cur.execute(sql)
                    conn.commit()
                    cur.close()
                    conn.close()
                    return redirect(url_for('planCollect', userID = userID))
        except:
            pass

        line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage(
                    alt_text='FlexMessage',
                    direction="ltr",
                    contents=BubbleContainer(
                        footer=BoxComponent(
                            layout='vertical',
                            spacing='sm',
                            contents=[
                                # callAction, separator, websiteAction
                                SpacerComponent(size='sm'),
                                # callAction
                                ButtonComponent(
                                    style='link',
                                    height='sm',
                                    action=URIAction(label='我的食譜', uri='{}/recipe_love/{}'.format(server_url,userID))),
                                # separator
                                SeparatorComponent(size='sm'),
                                # websiteAction
                                ButtonComponent(
                                    style='link',
                                    height='sm',
                                    action=URIAction(label='我的健身課表', uri='{}/plan_love/{}'.format(server_url,userID)))
                            ]
                        )
                    )
                )
        )

# ============================ 飲食日記 ===================================================
    elif 'diary' in query_string_dict:

        # 取出消息內User的資料
        user_profile = line_bot_api.get_profile(event.source.user_id)
        userID = str(user_profile.user_id)

        try:
            app.secret_key = 'youneverguess'



            #查詢
            @app.route('/diary/<userID>', methods = ['GET'])
            def record(userID):
                conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset='utf8')
                cur = conn.cursor()
                sql = """SELECT * FROM diary WHERE userID='{}' ORDER BY join_date DESC;""".format(userID)
                cur.execute(sql)
                u = cur.fetchall()
                conn.commit()

                #從資料庫叫出tdee
                sqlTdee = """SELECT tdee FROM members WHERE userID = '{}';""".format(
                    userID)

                cur.execute(sqlTdee)
                conn.commit()

                tdee = str(cur.fetchall()).rstrip(',)').lstrip('(')
                # print(tdee)

                #從資料庫算出當天已吃日期卡路里總和
                sqlCal = """SELECT SUM(food_calory) as total FROM diary WHERE userID = '{}' AND DATE(join_date) = CURDATE();""".format(
                    userID)

                cur.execute(sqlCal)
                conn.commit()
                foodCal = str(cur.fetchall()).lstrip('(Decimal(\'').rstrip('\'),)')
                # print(foodCal)

                #tdee-當天已吃卡路里總和，如果當天未輸入資料卡路里總和以0計算
                try:
                    remaining = float(tdee) - float(foodCal)

                except ValueError:
                    foodCal = 0
                    remaining = float(tdee) - float(foodCal)

                cur.close()
                conn.close()
                return render_template('diary.html', diary = u, userID = userID, tdee = float(tdee), foodcal = float(foodCal), remaining = remaining)


            #新增
            @app.route('/insert', methods = ['POST','GET'])
            def insert():
                if request.method == "POST":
                    flash("日記成功輸入！")
                    userID = request.form['userID']
                    food_name = request.form['food_name']
                    food_calory = request.form['food_calory']
                    #join_date = request.form['join_date']
                    join_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    conn = pymysql.connect(host = host, port = port, user = user, passwd = passwd, db = db)
                    cur = conn.cursor()
                    sql="""INSERT INTO diary (userID,food_name, food_calory, join_date) VALUES ('{}','{}','{}','{}');""".format(userID,food_name, food_calory, join_date)
                    cur.execute(sql)
                    conn.commit()
                    cur.close()
                    conn.close()
                    return redirect(url_for('record', userID = userID))





            #刪除
            @app.route('/kill', methods = ['POST','GET'])
            def killdiary():
                if request.method == 'POST':
                    userID = request.form['userID']
                    diary_id = request.form['diary_id']
                    flash("日記刪除成功！")
                    conn = pymysql.connect(host = host, port = port, user = user, passwd = passwd, db = db, charset = 'utf8')
                    cur = conn.cursor()
                    sql="""DELETE FROM diary WHERE diary_id={}""".format(diary_id)
                    cur.execute(sql)
                    conn.commit()
                    cur.close()
                    conn.close()
                    return redirect(url_for('record', userID = userID))



            #修改
            @app.route('/update',methods=['POST','GET'])
            def update():
                if request.method == 'POST':
                    userID = request.form['userID']
                    diary_id = request.form['diary_id']
                    food_name = request.form['food_name']
                    food_calory = request.form['food_calory']
                    #join_date = request.form['join_date']
                    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset='utf8')
                    cur = conn.cursor()
                    sql="""
                           UPDATE diary
                           SET food_name='{}', food_calory='{}'
                           WHERE diary_id='{}';
                        """.format(food_name, food_calory, diary_id)
                    flash("日記更新成功")
                    cur.execute(sql)
                    conn.commit()
                    cur.close()
                    conn.close()
                    return redirect(url_for('record', userID = userID))

# ============================ 健身日記 ===================================================
            #查詢
            @app.route('/sport/<userID>', methods=['GET'])
            def sportplan(userID):
                conn = pymysql.connect(host = host, port = port, user = user, passwd = passwd, db = db, charset = 'utf8')
                cur = conn.cursor()
                sql = """SELECT * FROM sport WHERE userID='{}' ORDER BY join_date DESC""".format(userID)
                cur.execute(sql)
                u = cur.fetchall()
                cur.close()
                conn.close()
                return render_template('sport.html', sport=u, userID = userID)

            #新增
            @app.route('/addin', methods=['POST', 'GET'])
            def addin():
                if request.method == "POST":
                    flash("日記成功輸入！")
                    userID = request.form['userID']
                    sport_name = request.form['sport_name']
                    sport_time = request.form['sport_time']
                    join_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    conn = pymysql.connect(host = host, port = port, user = user, passwd = passwd, db = db, charset = 'utf8')
                    cur = conn.cursor()
                    sql = """INSERT INTO sport (userID, sport_name, sport_time, join_date) VALUES ('{}','{}','{}','{}');""".format(
                        userID, sport_name, sport_time, join_date)
                    cur.execute(sql)
                    conn.commit()
                    cur.close()
                    conn.close()
                    return redirect(url_for('sportplan', userID = userID))

            #刪除
            @app.route('/vanish', methods=['POST', 'GET'])
            def vanishdiary():

                if request.method == 'POST':
                    sport_id = request.form['sport_id']
                    userID = request.form['userID']
                    flash("日記刪除成功！")
                    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset = 'utf8')
                    cur = conn.cursor()
                    sql = """DELETE FROM sport WHERE sport_id={};""".format(sport_id)
                    cur.execute(sql)
                    conn.commit()
                    cur.close()
                    conn.close()
                    return redirect(url_for('sportplan', userID = userID))

            #修改
            @app.route('/renew', methods=['POST', 'GET'])
            def renew():

                if request.method == 'POST':
                    userID = request.form['userID']
                    sport_id = request.form['sport_id']
                    sport_name = request.form['sport_name']
                    sport_time = request.form['sport_time']
                    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset='utf8')
                    cur = conn.cursor()
                    sql = """UPDATE sport
                                SET sport_name='{}', sport_time='{}'
                                WHERE sport_id='{}';
                        """.format(sport_name, sport_time, sport_id)

                    flash("日記更新成功")
                    cur.execute(sql)
                    conn.commit()
                    cur.close()
                    conn.close()
                    return redirect(url_for('sportplan', userID = userID))
        except:
            pass

            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(
                    alt_text='FlexMessage',
                    direction="ltr",
                    contents=BubbleContainer(
                        footer=BoxComponent(
                            layout='vertical',
                            spacing='sm',
                            contents=[
                                # callAction, separator, websiteAction
                                SpacerComponent(size='sm'),
                                # callAction
                                ButtonComponent(
                                    style='link',
                                    height='sm',
                                    action=URIAction(label='我的飲食日記', uri='{}'.format(server_url) + '/diary/{}'.format(userID))),
                                # separator
                                SeparatorComponent(size='sm'),
                                # websiteAction
                                ButtonComponent(
                                    style='link',
                                    height='sm',
                                    action=URIAction(label='我的健身課表', uri='{}'.format(server_url) + '/sport/{}'.format(userID)))

                            ]
                        )
                    )
                )
            )




# ==================================影像辨識=================================================

# 將消息模型，文字收取消息與文字寄發消息 引入
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage
)
'''
若收到圖片消息時，

先回覆用戶文字消息，並從Line上將照片拿回。
'''

@handler.add(MessageEvent, message=ImageMessage)
def handle_message(event):

    user_profile = line_bot_api.get_profile(event.source.user_id)
    userID = str(user_profile.user_id)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='照片辨識中．．．請稍後'))
    message_content = line_bot_api.get_message_content(event.message.id)
    with open('/app/image_recognition/image/'+userID+'.jpg', 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)

    result = photoIdentification(userID)

    #回覆使用者辨識結果
    line_bot_api.push_message('{}'.format(userID),
    TextSendMessage(text='{}'.format(result)))

'''

Application 運行（開發版）

'''
if __name__ == "__main__":
    app.run(host='0.0.0.0')
