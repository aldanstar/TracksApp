#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

class tools: #набор статических функций для расчета
    @staticmethod
    def img_by_name(name, progress=None):
        return os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), './images',name+'.png'))

    @staticmethod
    def commonString(string1, string2):
        answer = ""
        len1, len2 = len(string1), len(string2)
        for i in range(len1):
            match = ""
            for j in range(len2):
                if (i + j < len1 and string1[i + j] == string2[j]):
                    match += string2[j]
                else:
                    if (len(match) > len(answer)): answer = match
                    match = ""
        return answer

    @staticmethod
    def rgb_read(path):
        img = cv2.imread(path)
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    @staticmethod
    def rgb_read(path):
        img = cv2.imread(path)
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    @staticmethod
    def binnary2rgb(img:np.ndarray):
        img = np.argmax(img, axis=2)*255
        img = np.concatenate([img[...,None],img[...,None],img[...,None]], axis=2).astype(np.uint8)
        return img

    @staticmethod
    def filtBinnary(data, threshold):
        ret, thresh = cv2.threshold(data, threshold, 1, cv2.THRESH_BINARY)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (20, 20))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        return thresh


    @staticmethod
    def getContours(binimg):
        contours, hierarchy = cv2.findContours(binimg.copy(), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=lambda ctr: cv2.boundingRect(ctr)[1])
        return contours, hierarchy

    @staticmethod
    def calc_params(contour):
        # координаты описывающего прямоугольника
        x1, y1, w, h = cv2.boundingRect(contour)
        x2, y2 = x1 + w, y1 + h

        # копия контура
        copy = contour.copy()
        # смещение координат будущего слепка
        copy[:, :, 1] = copy[:, :, 1] - y1
        copy[:, :, 0] = copy[:, :, 0] - x1

        # подготавливаем шаблон слепка дефекта
        frame = np.zeros(((h, w))).astype(np.uint8)

        # заполнение шаблон слепка в пределах контура дефекта (остальное 0)
        cv2.drawContours(frame, [copy], contourIdx=0, color=(1, 1, 1), thickness=-1)

        # подсчет кол-ва 0 и 1 в слепке для вычисления площадей
        unique, counts = np.unique(frame, return_counts=True)
        elements = dict(zip(unique, counts))[1]

        return x1, x2, y1, y2, frame, copy, elements

    @staticmethod
    def semantic_segmentation(project, segmentation):
        '''Семантическая сегментация подгтовленного изображения'''
        sample = project.current_sample

        img = segmentation.predict(sample.prepared)
        size = float(sample.prepared.size)
        img = tools.filtBinnary(img, 0.75)

        img =  tools.binnary2rgb(img)

        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        contours, _ = tools.getContours(gray)
        for i, contour in enumerate(contours):
            left, rigth, top, bottom, frame, contour, elements = tools.calc_params(contour)
            area = round((float(elements)/size)*100, 2)
            sample.tracks.add_item(left, rigth, top, bottom, frame, contour, area)

    @staticmethod
    def counter(project, nnet):
        '''Семантическая сегментация подгтовленного изображения'''
        sample = project.current_sample

        for track in sample.tracks.get_sorted_by_id():

            frame = cv2.resize(track.frame, (416, 416))*255
            frame = frame[...,None][None,...]

            left = track.left
            rigth = track.rigth
            top = track.top
            bottom = track.bottom

            img = cv2.resize(sample.prepared[top:bottom,left:rigth], (416, 416))
            img = img[None,...]

            prediction = nnet.predict([img, frame])
            if prediction==0: prediction=1

            track.count = np.uint8(prediction)




        # img = nnet.predict(sample.prepared)
        # img = tools.filtBinnary(img, 0.75)
        #
        # img =  tools.binnary2rgb(img)
        #
        # gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        # contours, _ = tools.getContours(gray)
        # for i, contour in enumerate(contours):
        #     left, rigth, top, bottom, frame, contour = tools.calc_params(contour)
        #     sample.tracks.add_item(left, rigth, top, bottom, frame, contour)