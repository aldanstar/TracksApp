
import os
import cv2
from  app.tools import tools
import numpy as np
import matplotlib.pyplot as plt

def main():
    main_dir=os.path.normpath(u'E:\__TRACKS\SegmentationClass')
    second_dir = os.path.normpath(u'E:\__TRACKS\SegmentationObject')
    third_dir = os.path.normpath(u'E:\__TRACKS\JPEGImages')

    output = os.path.normpath(u'E:\__TRACKS\output')

    mask_out = os.path.join(output, 'mask')
    img_out = os.path.join(output, 'img')

    files = [file_name for file_name in os.listdir(main_dir)]

    try:
        for file in os.listdir(mask_out):
            os.remove(os.path.join(mask_out, file))

        for file in os.listdir(img_out):
            os.remove(os.path.join(img_out, file))

        os.rmdir(mask_out)
        os.rmdir(img_out)
    except FileNotFoundError:
        pass

    os.mkdir(mask_out)
    os.mkdir(img_out)

    for file_name in files:
    # file_name = 'SE1231@002.png'

        file_base = file_name.split('.')[0]

        file_jpg = '{}.jpg'.format(file_base)

        file_path = os.path.join(main_dir,file_name)

        second_path = os.path.join(second_dir, file_name)

        third_path = os.path.join(third_dir, file_jpg)

        img = cv2.imread(file_path)
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        gray = (gray/np.max(gray)).astype(np.uint8)

        contours, _ = tools.getContours(gray)

        img2 = cv2.imread(second_path)
        rgb = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)

        img3 = cv2.imread(third_path)
        rgb2 = cv2.cvtColor(img3, cv2.COLOR_BGR2RGB)

        for i, contour in enumerate(contours):
            left, rigth, top, bottom, frame, contour = tools.calc_params(contour)
            new = rgb[top:bottom,left:rigth]*frame[...,None]
            new2 = rgb2[top:bottom,left:rigth]

            count = np.unique(cv2.cvtColor(new, cv2.COLOR_RGB2GRAY)).size - 1
            if new2.shape<(10, 10, 3) or count==0:
                break




            frame = cv2.resize(frame, (416, 416))
            new2 = cv2.resize(new2, (416, 416))




            frame = frame*255
            new2 = cv2.cvtColor(new2, cv2.COLOR_RGB2BGR)

            cv2.imwrite(os.path.join(mask_out, '{}_{}_{}.png'.format(file_base,i,count)), frame.astype(np.uint8))
            cv2.imwrite(os.path.join(img_out, '{}_{}_{}.png'.format(file_base,i,count)), new2.astype(np.uint8))



if __name__ == '__main__':
    main()