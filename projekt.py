# -*- coding: utf-8 -*-
"""Projekt.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1aw7NNfUKrvWbFU-DdHkjTxW4XS-FBXkv

Tworzenie ścieżki dostępu do danych
"""

! curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
! sudo apt-get install git-lfs
! git lfs install
! git clone https://github.com/neheller/kits19.git

"""Wczytywanie danych"""

# Commented out IPython magic to ensure Python compatibility.
# %cd kits19
! python -m starter_code.get_imaging

"""Wczytanie potrzebnych bibliotek."""

# Commented out IPython magic to ensure Python compatibility.
import os
# %cd /content/kits19
from starter_code.utils import load_case
import matplotlib.pyplot as plt
from imageio import imwrite
from pathlib import Path
import argparse
import scipy.misc
import numpy as np
import os
import skimage.io as io
import skimage.transform as trans
from keras.models import *
from keras.layers import *
from keras.optimizers import *
from keras.callbacks import ModelCheckpoint, LearningRateScheduler
from keras import backend as keras
import skimage.measure as measure
from skimage.transform import resize
from sklearn.model_selection import train_test_split

"""Wczytywanie zdjęć do folderów"""

# Commented out IPython magic to ensure Python compatibility.
for i in range(1,10):
#   %cd /content/kits19/visualized
  volume, segemnatation=load_case('case_0000'+str(i))
  
  os.mkdir("masks_0000" +str(i))
  os.mkdir("images_0000"+str(i))
  mask_out_path = Path("/content/kits19/visualized/masks_0000"+str(i))
  image_out_path = Path("/content/kits19/visualized/images_0000"+str(i))
  s=segemnatation.get_fdata()
  v=volume.get_fdata()

  for j in range(s.shape[0]):  
    maskfpath = mask_out_path / ("{:05d}.png".format(j))
    imagefpath = image_out_path / ("{:05d}.png".format(j))
    imwrite(str(maskfpath), s[j,:,:])
    imwrite(str(imagefpath), v[j,:,:])

"""Przygotowywanie danych do trenowania i testów. Zmniejszenie wielkosci obrazów i określenie ilosci wsadowych case-ów."""

# Commented out IPython magic to ensure Python compatibility.
# %cd kits19/

IMG_WIDTH = 128
IMG_HEIGHT = 128

X = np.zeros((0, IMG_HEIGHT, IMG_WIDTH,1))
Y = np.zeros((0, IMG_HEIGHT, IMG_WIDTH,1))

for n in range (1,2):
    if (n<10):
        volume, segementation=load_case('case_0000'+str(n))
    if (10<=n<100):
        volume, segementation=load_case('case_000'+str(n))
    if (100<=n<200):
        volume, segementation=load_case('case_00'+str(n))
        
    
    v=volume.get_fdata()
    s=segementation.get_fdata()
    X_temp = np.zeros((v.shape[0], IMG_HEIGHT, IMG_WIDTH,1))
    Y_temp = np.zeros((v.shape[0], IMG_HEIGHT, IMG_WIDTH,1))
    
       
    for i in range (s.shape[0]): 
        img= v[i,:,:]
        img = resize(img, (IMG_HEIGHT, IMG_WIDTH,1), mode='constant', preserve_range=True)
        X_temp[i] = img 
 
        mask = s[i,:,:]
        mask = resize(mask, (IMG_HEIGHT, IMG_WIDTH,1), mode='constant', preserve_range=True)
        Y_temp[i] = mask
        
    X=np.concatenate((X, X_temp), axis=0)   
    Y=np.concatenate((Y, Y_temp), axis=0)

X_train,X_test,y_train,y_test = train_test_split(X,Y,test_size=0.3)

"""Architektura sieci"""

def uNet(pretrained_weights=None,input_size=(128,128,1)):
  inputs = Input(input_size)
  conv1=Conv2D(64,3,activation='relu',padding='same',kernel_initializer='he_normal')(inputs)
  conv1=Conv2D(64,3,activation='relu',padding='same',kernel_initializer='he_normal')(conv1)
  pool1=MaxPooling2D(pool_size=(2,2))(conv1)
  conv2 = Conv2D(128, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(pool1)
  conv2 = Conv2D(128, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv2)
  pool2 = MaxPooling2D(pool_size=(2, 2))(conv2)
  conv3 = Conv2D(256, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(pool2)
  conv3 = Conv2D(256, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv3)
  pool3 = MaxPooling2D(pool_size=(2, 2))(conv3)
  conv4 = Conv2D(512, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(pool3)
  conv4 = Conv2D(512, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv4)
  drop4 = Dropout(0.5)(conv4)
  pool4 = MaxPooling2D(pool_size=(2, 2))(drop4)

  conv5 = Conv2D(1024, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(pool4)
  conv5 = Conv2D(1024, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv5)
  drop5 = Dropout(0.5)(conv5)

  up6 = Conv2D(512, 2, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(UpSampling2D(size = (2,2))(drop5))
  merge6 = concatenate([drop4,up6], axis = 3)
  conv6 = Conv2D(512, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(merge6)
  conv6 = Conv2D(512, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv6)

  up7 = Conv2D(256, 2, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(UpSampling2D(size = (2,2))(conv6))
  merge7 = concatenate([conv3,up7], axis = 3)
  conv7 = Conv2D(256, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(merge7)
  conv7 = Conv2D(256, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv7)

  up8 = Conv2D(128, 2, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(UpSampling2D(size = (2,2))(conv7))
  merge8 = concatenate([conv2,up8], axis = 3)
  conv8 = Conv2D(128, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(merge8)
  conv8 = Conv2D(128, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv8)

  up9 = Conv2D(64, 2, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(UpSampling2D(size = (2,2))(conv8))
  merge9 = concatenate([conv1,up9], axis = 3)
  conv9 = Conv2D(64, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(merge9)
  conv9 = Conv2D(64, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv9)
  conv9 = Conv2D(2, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv9)
  conv10 = Conv2D(1, 1, activation = 'sigmoid')(conv9)

  model = Model(input = inputs, output = conv10)

  model.compile(optimizer = Adam(lr = 1e-4), loss = 'binary_crossentropy', metrics = ['accuracy'])
    
  model.summary()

  if(pretrained_weights):
    model.load_weights(pretrained_weights)

  return model

"""Proces trenowania sieci oraz zapisywanie wag składowych warstw."""

model = uNet()
model_checkpoint = ModelCheckpoint('unet_kidney_weights.hdf5', monitor='loss',verbose=1, save_best_only=True)
model.compile(loss='binary_crossentropy', metrics=['accuracy'], optimizer='adam')
model.fit(X_train, x_test,batch_size=2, nb_epoch=100, verbose=1,validation_split=0.2, shuffle=False, callbacks=[model_checkpoint])
model.load_wegihts(model_checkpoint)

"""Predykcja modelu"""

results = model.predict(x_test)

"""Przedstawienie graficzne procesu trenowania."""

plt.figure()
plt.title("Krzywa progresu uczenia")
plt.plot(result.history["loss"],label='loss')
plt.plot(result.history["val_loss"],label='val_loss')
plt.plot(np.argmin(result.history['val_loss']), np.min(result.history['val_loss']),marker='x',color='r',label='best model')
plt.xlabel("Epochs")
plt.ylabel('log_loss')
plt.legend()

"""Funkcja do ewaluacji - wskaźnik Jaccard index zarówno nerka i guz"""

def evaluation(target,prediction):
  score_t=[]
  score_k=[]

  prediction_k=np.equal(prediction,1)
  prediction_t=np.equal(prediction,2)

  target_k=np.equal(target,1)
  target_t=np.equal(target,2)

  for i in range (target.shape[0]):
     intersection_t = np.logical_and(target_t[i,:,:,:], prediction_t[i,:,:,:])
     union_t = np.logical_or(target_t[i,:,:,:], prediction_t[i,:,:,:])
     intersection_k = np.logical_and(target_k[i,:,:,:], prediction_k[i,:,:,:])
     union_k = np.logical_or(target_k[i,:,:,:], prediction_k[i,:,:,:])

     if np.sum(union_t)!=0:
       jac_t = np.sum(intersection_t)/np.sum(union_t)
       score_t.append(jac_t)

     if np.sum(union_k)!=0:
       jac_k = np.sum(intersection_k)/np.sum(union_k)
       score_k.append(jac_k)

  return np.mean(score_t), np.mean(score_k)
  
c1, c2= evaluation(y_test,results)
print("Jaccard index for tumor: ", c1)
print("Jaccard index for kidney: ", c2)