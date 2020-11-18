#import pymongo
import json
import numpy as np
import logging  # Setting up the loggings to monitor gensim
logging.basicConfig(format="%(levelname)s - %(asctime)s: %(message)s", datefmt= '%H:%M:%S', level=logging.INFO)
#from sklearn.manifold import TSNE
from numpy import dot
from numpy.linalg import norm
from gensim.models import word2vec
import time
#start_time = time.time()


# user prefered ingredient
def user_vector(list_ingred):
    model = word2vec.Word2Vec.load("/app/recipe_recommend/recipevec2.model")

    # calculate user-prefered ingredients total vector
    wordvec = np.zeros([1,150], dtype = float)
    for item in list_ingred:
        try:
            wordvec = wordvec + model[item]
        except:
            pass
    avgvec = wordvec / len(list_ingred)
    return avgvec

def cosine_distance_uservec(uservec, target_list, num):

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
        inser_value = (cos_sim, url, img_url, recipe_no)
        cosine_dict[item['title']] = inser_value


    dist_sort = sorted(cosine_dict.items(), key=lambda dist: dist[1][0], reverse=True)  ## in Descedning order
    for item in dist_sort:
        word_list.append((item[0], item[1]))
    return word_list[0:num]


def main(list_ingredient):

#### =========== Read recipe vector from mongoDB ====================
    # # Create connnect 建立與mongoDB連線
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
    with open('/app/recipe_recommend/recipe_vector_full.json', 'r', encoding='utf-8') as file:
        txt = file.readlines()

    target_list = []
    for each_item in txt:
        target_list.append(json.loads(each_item))



    my_prefer = user_vector(list_ingredient)
    callback = cosine_distance_uservec(my_prefer, target_list, 100)

    #print("--- spend %s seconds ---" % (time.time() - start_time))
    return callback


if __name__ == '__main__':

    prefer_ingredient = ['雞胸肉', '花椰菜', '黑胡椒粉', '酪梨', '香蕉']
    end_result = main(prefer_ingredient)
    print(end_result)
