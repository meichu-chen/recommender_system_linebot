from keras.models import load_model
import numpy as np
import os
import cv2
from PIL import Image
import matplotlib.pyplot as plt
import time
#import keras.backend.tensorflow_backend as tb


#tensorflow-gpu==2.2.0
#keras==2.3.1

def photoIdentification (userID):

    os.environ["CUDA_VISIBLE_DEVICES"]="-1"

#    tb._SYMBOLIC_SCOPE.value = True
# 計算建立模型的時間(起點)
    # start = time.time()

    #image folder
    file_path = "/app/image_recognition/image/{:s}.jpg".format(userID) #每種器材測試5張(圖片來源不同)，測試後成功辨識率為100%；實地拍攝辨識成功率：54.84%

    #dimesions of images
    img_width,img_height = 299,299
    class inception_retrain(object):
        def __init__(self):
            self.img=None
            self.model=None
            self.InV3model=None
        def _load_image(self,img):
            '''Takes an image
                Returns its proper form to feed into model's predcition '''
            # image = cv2.imread('test/{}'.format(img))
            fd = open(img,'rb')
            img_str = fd.read()
            fd.close()
            nparr = np.fromstring(img_str, np.uint8)
            image = cv2.imdecode(nparr, -1)[:,:,:3] #imdecode flag = -1 Unchanged
            image = cv2.resize(image, (299, 299))
            image = np.expand_dims(image/255, axis=0)
            image = np.vstack([image])
            return image
        def _feature_extraction_inception(self,img):
            image=self._load_image(img)
            self.img=image
            features=self.InV3model.predict(image)
            return features
        def _load_model(self):
            if self.model is None:
                self.model=load_model('/app/image_recognition/model_CnnModelTrainWorkout_v3_5calsses.h5')
            if self.InV3model is None:
                self.InV3model=load_model("/app/image_recognition/inception.h5")
        def predict(self,img):
            '''Takes an imagebbb
               Return the predicted probabilities for each class'''
            self._load_model()
            image=self._feature_extraction_inception(img)
            self.img=image
            pred=self.model.predict(image)
            # pred=np.round(pred,3).reshape(4,)
            pred=np.round(pred,5).reshape(5,) #有5個class
            # return pred[0],pred[1],pred[2],pred[3]
            return pred[0],pred[1],pred[2],pred[3],pred[4]
            # print(pred[0],pred[1],pred[2],pred[3],pred[4])

    def model_check():
        label = ['Dumbbell','Rowing boat machine', 'Cable crossover', 'Pullback machine', 'Barbell bench press machine']
        Predlist = list()
        model = inception_retrain()
        pred1, pred2, pred3, pred4, pred5 = model.predict(file_path)
        Predlist.append(pred1)
        Predlist.append(pred2)
        Predlist.append(pred3)
        Predlist.append(pred4)
        Predlist.append(pred5)
        # print(Predlist) 測試用
        return label[Predlist.index(max(Predlist))] #取得a最大的index

    a = model_check()

    #辨識健身器材後，提供相對應的教學影片路徑
    if a == 'Dumbbell':
        result = '辨識結果為：啞鈴，請參考以下教學網站：https://www.hiyd.com/dongzuo/?equipment=8'
        print(result)
    elif a == 'Rowing boat machine':
        result = '辨識結果為：划船機，請參考以下教學網站：https://www.hiyd.com/dongzuo/?equipment=34'
        print(result)
    elif a == 'Cable crossover':
        result = '辨識結果為：龍門架，請參考以下教學網站：https://www.hiyd.com/dongzuo/?equipment=32'
        print(result)
    elif a == 'Pullback machine':
        result = '辨識結果為：拉背機，請參考以下教學網站：https://www.hiyd.com/dongzuo/?equipment=35'
        print(result)
    else:
        result = '辨識結果為：槓鈴臥推機，請參考以下教學網站：https://www.hiyd.com/dongzuo/?equipment=10&muscle=9'
        print(result)

    return result

    #計算建立模型的時間(終點)
    # end = time.time()
    # spend = end - start
    # hour = spend // 3600
    # minu = (spend - 3600 * hour) // 60
    # sec = int(spend - 3600 * hour - 60 * minu)
    # print(f'一共花費了{hour}小時{minu}分鐘{sec}秒')

    # im = Image.open(file_path)
    # im_list = np.asarray(im)
    # plt.title("Result: There is a {}".format(a))
    # plt.axis("off")
    # plt.imshow(im_list)
    # plt.show()

if __name__ == '__main__':
    photoIdentification('test')
