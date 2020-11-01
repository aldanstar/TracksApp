from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras import backend as K
from res import resources
import numpy as np
import cv2

class counter:

    def __init__(self, ):
        self.model = load_model(resources.CNTNN)

        self.data_info= {
            'orig_width' : None,
            'orig_height' : None,
            'img_width' : 416,
            'img_height' : 416,
            'num_classes' : 20,
        }

    def predict(self, orig_imgs):
        prediction = self.model.predict(orig_imgs)
        return np.argmax(prediction)

class imgsep:

    def __init__(self, ):
        self.model = load_model(resources.SEPNN)

        self.data_info= {
            'orig_width' : None,
            'orig_height' : None,
            'img_width' : 416,
            'img_height' : 416,
            'num_classes' : 2,
        }

    def predict(self, orig_imgs):
        imgs=[]
        for img in orig_imgs:
            img = image.img_to_array(image.load_img(img, target_size=(self.data_info['img_width'], self.data_info['img_height'])))
            imgs.append(img)
        imgs=np.array(imgs)
        prediction = self.model.predict(imgs)
        predict_list = np.argmax(prediction, axis = 1)
        result = [x for _,x in sorted(zip(predict_list,orig_imgs))]
        return result

class imgsemseg:

    def __init__(self):
        self.model = load_model(resources.SEGNN, custom_objects={"dice_coef": self.dice_coef})

        self.data_info= {
            'orig_width' : None,
            'orig_height' : None,
            'img_width' : 416,
            'img_height' : 416,
            'num_classes' : 2,
        }

    def dice_coef(self, y_true, y_pred):
        return (2. * K.sum(y_true * y_pred) + 1.) / (K.sum(y_true) + K.sum(y_pred) + 1.)

    def predict(self, orig_img):
        self.data_info['orig_width'] = orig_img.shape[1]
        self.data_info['orig_height'] = orig_img.shape[0]

        img = cv2.resize(orig_img, (int(self.data_info['img_width']), int(self.data_info['img_height'])))
        prediction = self.model.predict(img[None,...])

        orig_prediction = []
        for predict in prediction:
            some = cv2.resize(predict, (int(self.data_info['orig_width']), int(self.data_info['orig_height'])))
            orig_prediction.append(some)
        orig_prediction = np.array(orig_prediction)

        if orig_prediction.shape[0] == 1:
                orig_prediction = orig_prediction[0]

        return orig_prediction