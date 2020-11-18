'''
#迴圈讀取本地列表，
#上傳設定檔，取得id，並將id寫入檔案中，而後上傳圖片

'''

import json
from linebot import LineBotApi


'''
#rich_menu的本地列表
'''
rich_menu_array = ['rich_menu_0', 'rich_menu_1', 'rich_menu_2', 'rich_menu_3']


# 載入安全設定檔
secretFileContentJson = json.load(open("./line_secret_key", 'r', encoding='utf8'))
line_bot_api = LineBotApi(secretFileContentJson.get("channel_access_token"))

from linebot.models import RichMenu

for rich_menu_name in rich_menu_array:
    # 創建菜單，取得menuId
    lineRichMenuId = line_bot_api.create_rich_menu(rich_menu=RichMenu.new_from_json_dict(
        json.load(open("素材/" + rich_menu_name + '/rich_menu.json', 'r', encoding='utf8'))))
    print("-設定檔上傳結果")
    print(lineRichMenuId)

    # id寫入本地端
    f = open("素材/" + rich_menu_name + "/rich_menu_id", "w", encoding='utf8')
    f.write(lineRichMenuId)
    f.close()

    # 上傳照片至該id
    set_image_response = ''
    with open("素材/" + rich_menu_name + '/rich_menu.jpg', 'rb') as f:
        set_image_response = line_bot_api.set_rich_menu_image(lineRichMenuId, 'image/jpeg', f)

    print("-圖片上傳結果")
    print(set_image_response)
