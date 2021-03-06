# -*- coding: utf-8 -*-
"""ciltkanseri.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ub-btoC85zpYDd053vLX27gbmlmWPURx
"""

# kütüphaneleri tanımlıyoruz
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import cv2 as cv
import seaborn as sns

# drşve a erişim sağlıyoruz
from google.colab import drive
drive.mount('/content/drive')

data = pd.read_csv('/content/drive/My Drive/HAM10000_metadata.csv') # drive içinde ki veriseti yolunu veriyoruz

data # veri setini görüyoruz

data=data.drop(columns=['lesion_id']) # lesion id siliyoruz istersek silmeyebiliriz yük olmasın diye... ve karışmasın diye. silinmesi mantıklı olan...

veri=data.sample(7) # 7 adet rastegele veri seçiyoruz dataset içerisinden

veri #görüntülüyoruz rastgele gelen değerleri

sns.countplot(veri['dx']) #rastegele seçilen verilerin dx değerlerini grafikte görüyuoruz.

PATH='/content/drive/My Drive/HAM10000_images' # resim klasörü yolunu belirtiyoruz

count=0
count2=0
image_value=[]
# for olmazsa hata alıruz öçünkü birden fazla resim alınacak...
for row in data.iterrows():
    # 6 adet resim okunsun dedik doğru değer buıdur
    if count2<=6:
      i_name='ISIC_000000'+str(count2)+'.jpg' # resimlerin isimlerihni belli algoritma ile aldık
      count2=count2+1
    else:
      break
      #dosyayı aldık ve resimleri okuduk.
    PA=os.path.join(PATH,i_name)
    img_arr=cv.imread(PA,1)

    try:
      img_arr=cv.resize(img_arr,(100,100)) # yeniden boyutlandırma işlemi yaptık.
    except:
      continue
# görüntü işleme için renklendirme işlemi yaptık. siyah beyaz vs.
    img_arr=cv.cvtColor(img_arr,cv.COLOR_BGR2RGB)
    image_value.append([img_arr,veri]) # rsimleri listeye ekledik.
    #görmek için gerekli kod
    plt.imshow(img_arr)
    plt.show() 
    # 6 olunca dur dedik
    if count==6:
        break
    count+=1

len(image_value)

import random
random.shuffle(image_value) # listeyi karıştırmak için kullanılan kod. rastegele vs

#dx değerini ve gelen rastgele veri dizisini for ile lşisteye atadık

X=[]

y=[]

for feature,label in image_value:
  X.append(feature)
  y.append(veri.dx)
len(X),len(y)

y # dx değerlerini görüyoruz.

from sklearn.preprocessing import LabelEncoder
# verileri sayısallaştırıyoruz. dx değerlerine belli rakamlar veriyoruz. veriyi işlemek için sklearn kütüphanesi mantığı
for i in y:
  lbl=LabelEncoder()
  y=lbl.fit_transform(i)
  y.shape

y # verilen sayıları değerleri görüyoruz

from sklearn.model_selection import train_test_split # test eğitim için gerekli kütüphane

train_X,test_X,train_y,test_y=train_test_split(X,y,test_size=0.2)  #test ve eğitim yapıyoruz

# kategorileştirme yapıyoruz... eğitimi kategorileştiriyoruz

from tensorflow.keras.utils import to_categorical

one_hot_train=to_categorical(train_y)
one_hot_train

#testi kategorileştirme yapıyoruz

one_hot_test=to_categorical(test_y)
one_hot_test

#diziyi yeniden şekillendirme
train_X=np.array(train_X).reshape(-1,100,100,3)
train_X=train_X/255.0
test_X=np.array(test_X).reshape(-1,100,100,3)
test_X=test_X/255.0

train_X.shape,test_X.shape,one_hot_train.shape,one_hot_test.shape

# gerekli kütüphaneleri ekliyoruz
from keras.models import Sequential,Input,Model
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
from tensorflow.keras.layers import BatchNormalization
from keras.layers.advanced_activations import LeakyReLU
#from tensorflow.keras.callbacks import History as history

# Bir Sequentialmodel, her katmanın tam olarak bir giriş tensörüne ve bir çıkış tensörüne sahip olduğu düz bir katman yığını için uygundur .

# keras içim model eğitimi seçini denilebilir

model = Sequential()
model.add(Conv2D(32, kernel_size=(3, 3),activation='relu',input_shape=(100,100,3),padding='same'))
model.add(MaxPooling2D((2, 2),padding='same'))
model.add(Dropout(0.20))

model.add(Conv2D(64, (3, 3), activation='relu',padding='same'))
model.add(MaxPooling2D(pool_size=(2, 2),padding='same'))
model.add(Dropout(0.40))

model.add(Conv2D(128, (3, 3), activation='relu',padding='same'))
model.add(LeakyReLU(alpha=0.1))                  
model.add(MaxPooling2D(pool_size=(2, 2),padding='same'))
model.add(Dropout(0.20))

'''model.add(Conv2D(256, (3, 3), activation='relu',padding='same'))
model.add(LeakyReLU(alpha=0.1))                  
model.add(MaxPooling2D(pool_size=(2, 2),padding='same'))
model.add(Dropout(0.40))'''

model.add(Flatten())

model.add(Dense(64, activation='linear'))
model.add(LeakyReLU(alpha=0.1))
model.add(Dense(128, activation='linear'))
model.add(Dense(256, activation='linear'))
model.add(Dense(7, activation='softmax'))
model.summary()

# modeli compile ediyoruz. derliyoruz yani...

model.compile(optimizer='adam',loss='sparse_categorical_crossentropy',metrics=['accuracy'])
#train_y modelini alcaz
history=model.fit(train_X,train_y,batch_size=128,epochs=10,validation_split=0.2) # ve sşimdi de modeli eğitiyıoruz... historiy içine atıyopruz

test_loss,test_acc=model.evaluate(test_X,test_y) # modeli değerlendiiroyruz. test işlemlerini

# sonuıçları grafiğe döküğyoruz

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model Loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['train','test'],loc='upper left')
plt.show()

# sonuçları grafiğe döküyoruz.

plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Model Accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['train','test'],loc='upper left')
plt.show()