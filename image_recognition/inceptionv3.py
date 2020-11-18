from keras.applications.inception_v3 import InceptionV3
from keras.layers import Dense,GlobalAveragePooling2D,BatchNormalization
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential, Model
import numpy as np
import matplotlib.pyplot as plt
from PIL import ImageFile
import time
import tensorflow as tf

#读取图像出现”image file is truncated“错误
#PIL读取了未上传完的图片，即图中有些数据缺失。可以通过一个设置使其接受这一点。
ImageFile.LOAD_TRUNCATED_IMAGES = True

#TensorFlow 默認情況下會映射幾乎所有GPU內存，所以需在運行時分配內存
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
	# Currently, memory growth needs to be the same across GPUs
	try:
		for gpu in gpus:
			tf.config.experimental.set_memory_growth(gpu, True)
	except RuntimeError as e:
		print(e)

def feature_extraction_InV3(img_width, img_height,
                        train_data_dir,
                        num_image,
                        epochs):
    base_model = InceptionV3(input_shape=(299, 299, 3),
                              weights='imagenet', include_top=False)
    x = base_model.output
    x = GlobalAveragePooling2D()(x)

    model = Model(inputs=base_model.input, outputs=x)

    train_generator = ImageDataGenerator(rescale=1. / 255).flow_from_directory(train_data_dir,
    target_size = (299, 299),
    batch_size = 15,
    class_mode = "categorical",
    shuffle=False)

    y_train=train_generator.classes
    y_train1 = np.zeros((num_image, 5))
    y_train1[np.arange(num_image), y_train] = 1

    train_generator.reset
    X_train=model.predict_generator(train_generator,verbose=1)
    print (X_train.shape,y_train1.shape)
    return X_train,y_train1,model

def train_last_layer(img_width, img_height,
                        train_data_dir,
                        num_image,
                        epochs = 50):
    X_train,y_train,model=feature_extraction_InV3(img_width, img_height,
                            train_data_dir,
                            num_image,
                            epochs)

    X_test,y_test,model=feature_extraction_InV3(img_width,img_height,
                            test_data_dir,
                            num_test_image,
                            epochs)

    my_model = Sequential()
    my_model.add(BatchNormalization(input_shape=X_train.shape[1:]))
    my_model.add(Dense(1024, activation = "relu"))
    my_model.add(Dense(5, activation='softmax'))
    my_model.compile(optimizer="SGD", loss='categorical_crossentropy',metrics=['accuracy'])
    #early = EarlyStopping(monitor='val_loss', min_delta=0, patience=10, verbose=1, mode='auto')
    # my_model.fit(X_train, y_train,epochs=18,batch_size=30,verbose=1)
    history = my_model.fit(X_train, y_train,epochs=20,
                 validation_data=(X_test,y_test),
                 # validation_split=0.2, #切割20%訓練集做validataion
                 # shuffle=1,
                 batch_size=30,verbose=1)
    # plot_training(history,'./')
    my_model.save('model_CnnModelTrainWorkout_v3_5calsses.h5')
    return history

def plot_training(history_ft):
    print(history_ft.history.keys())
    acc = history_ft.history['accuracy']
    val_acc = history_ft.history['val_accuracy']
    loss  = history_ft.history['loss']
    val_loss = history_ft.history['val_loss']
    epoches = range(len(acc))
    plt.plot(epoches,acc,'r',color ='green',label = 'acc')
    plt.plot(epoches,val_acc,'--r',label = 'val_acc') #default color
    plt.title('Training and Validataion accuracy')
    plt.figure()
    plt.plot(epoches,loss,'r',color = 'green',label = 'loss')
    plt.plot(epoches,val_loss,'--r',label = 'val_loss')
    plt.title('Training and Validataion loss')
    plt.savefig('path_5classes')  # Save the current figure.plt.savefig('path') #Save the current figure.
    plt.show()
    print('acc:',acc)
    print('val_acc:',val_acc)
    print('epoches:',range(len(acc)))
    print('loss:',loss)
    print('val_loss',val_loss)

if __name__=="__main__":
    img_width=299
    img_height = 299
    train_data_dir = "./vgg16/train"
    test_data_dir = "./vgg16/test"
    num_image= 4800
    num_test_image = 1200
    epochs = 10

    # 計算建立模型的時間(起點)
    start = time.time()

    model=train_last_layer(img_width, img_height,
                            train_data_dir,
                            num_image,epochs)

    # 計算建立模型的時間(終點)
    end = time.time()
    spend = end - start
    hour = spend // 3600
    minu = (spend - 3600 * hour) // 60
    sec = int(spend - 3600 * hour - 60 * minu)
    print(f'一共花費了{hour}小時{minu}分鐘{sec}秒')

    plot_training(model)