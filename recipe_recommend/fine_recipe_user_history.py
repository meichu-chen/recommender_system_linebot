#import pymongo
import json
import numpy as np
import logging  # Setting up the loggings to monitor gensim
logging.basicConfig(format="%(levelname)s - %(asctime)s: %(message)s", datefmt= '%H:%M:%S', level=logging.INFO)
#from sklearn.manifold import TSNE
from numpy import dot
from numpy.linalg import norm
#from gensim.models import word2vec
import time
start_time = time.time()


# user prefered ingredient
def user_vector(list_history):
    '''
    This function takes user's favortie recipes, and calculate their mean vector.
    :param list_history: A list, list of user favorite recipes history
    :return: Numpy array and a list. User vector(array[1,150]), and all recipes list
    '''
## ============ Read recipe vector from MongoDB ========================
    # #Create connnect 建立與mongoDB連線
    # client = pymongo.MongoClient(host='localhost', port=27017)
    #
    # # assign database 選擇資料庫
    # db = client.capstone
    # # assign colection 選擇collection
    # collection = db.recipe_wordvec_2
    #
    # # Query specific column from all recipe_raw 選擇要讀取的資料欄位
    # queryArgs = {}
    # projectField = {'url': True, 'img_url': True, 'title': True, 'wordvec': True}
    # search_response = db.recipe_wordvec_2.find(queryArgs, projection=projectField)
    #
    # target_list = []
    # for item in search_response:
    #     target_list.append(item)

#### ====== Read recipe vecto from json file  ===============================
    with open('./recipe_vector_full.json', 'r', encoding='utf-8') as file:
        txt = file.readlines()

    target_list = []
    for each_item in txt:
        target_list.append(json.loads(each_item))

    wordvec = np.zeros([1, 150], dtype=float)
    for n, item in enumerate(list_history):
        for check in target_list:
            if item == check['title']:
                wordvec = wordvec + check['wordvec']
                break
    avgvec = wordvec / len(list_history)
    return avgvec, target_list

def cosine_distance_userhistory(uservec, target_list, num):
    '''
    This function takes user vector, and all recipes, find the most similar recipes in database
    :param uservec: Numpy array. A shape of (1,150) array, that represents user preference
    :param target_list: A list, list of all recipes in database
    :param num: Int. number of desired return recommended recipes
    :return: A list, list of "num" tuples, consist of recipe title and similarity
    '''

    cosine_dict = {}
    word_list = []

    # 找尋並取得所輸入菜單的總向量

    a = uservec
    # a = model[word]
    for item in target_list:
        # if item['title'] != word : # 不跟自己做餘弦相似度計算
        # b = model [item]

        url = item['url']
        img_url = item['img_url']
        recipe_no = item['recipe_no']
        b = item['wordvec']
        cos_sim = dot(a, b) / (norm(a) * norm(b))
        inser_value = (cos_sim, url, img_url,recipe_no)
        cosine_dict[item['title']] = inser_value
    dist_sort = sorted(cosine_dict.items(), key=lambda dist: dist[1][0], reverse=True)  ## in Descedning order
    for item in dist_sort:
        word_list.append((item[0], item[1]))
    return word_list[0:num]


def main(list_ingredient):
    '''
    Main function
    :param list_ingredient: A list, list of user favorite recipes
    :return: Print out recommended recipes
    '''

    my_prefer, target_list = user_vector(list_ingredient)
    callback = cosine_distance_userhistory(my_prefer, target_list, 10)
    print(callback)
    print("--- spend %s seconds ---" % (time.time() - start_time))
    return callback

if __name__ == '__main__':

    prefer_ingredient = ['【食材測試】低卡裸麥黑麵包','[蛋奶素/減脂]青江菜烘蛋（無五辛）','檸檬鯛魚片，泰式減肥餐',
             '【養生煮食】涼拌秋葵山藥　改善胃食道逆流','涼拌鮪魚蛋淺漬高麗菜〞免動火低醣涼拌菜']
    main(prefer_ingredient)

