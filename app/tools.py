#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import cv2
import numpy as np

class tools: #набор статических функций для расчета

    @staticmethod
    def normalize(arr: np.ndarray) -> np.ndarray:
        '''нормализация к1 канального избражения от 0 до 255'''
        arr = np.float16(arr)
        amin = arr.min()
        rng = arr.max() - amin
        return ((arr - amin) * 255 / rng).astype(np.uint8)

    @staticmethod
    def normalize_img(arr: np.ndarray) -> np.ndarray:
        '''нормализация для каждого канала'''
        bands = []
        for i in range(arr.shape[2]):
            bands.append(tools.normalize(np.array(arr)[:, :, i]))
        return np.dstack(bands)

    @staticmethod
    def norm_l_extract(img: np.ndarray) -> np.ndarray:
        '''выделение канала светлоты из цветового пространства Lab'''
        if not isinstance(img, np.ndarray):
            img = np.array(img)
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        cl = cv2.equalizeHist(cl)
        return tools.normalize(cl)

    @staticmethod
    def mean_bet_imgs(img1: np.ndarray, img2: np.ndarray) -> np.ndarray:
        '''создание дополнительного третьего канала'''
        if not isinstance(img1, np.ndarray):
            img1 = np.array(img1)
            img2 = np.array(img2)
        img1 = tools.normalize_img(img1)
        img2 = tools.normalize_img(img2)
        img3 = np.mean(np.dstack((img1, img2)), axis=2)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        img3 = clahe.apply(tools.normalize(img3))
        img3 = cv2.equalizeHist(img3)
        return tools.normalize(img3)

    @staticmethod
    def processing(path_to_file, project, separator_net, segmentation_net, counter_net):
        '''Процедура обработки изображений'''
        # Ищем похожие файлы
        files=tools.findSame(path_to_file)

        # Определение типа изображений
        backlight_path, through_path = separator_net.predict(files)

        through = tools.rgb_read(through_path)
        backlight = tools.rgb_read(backlight_path)

        # Поиск общей части из названий изображений для наименования образца в проекте
        name = tools.commonString(os.path.basename(files[0]),os.path.basename(files[1]))

        if name not in project.get_samples_names():
            project.samples.add_item(name,through,backlight)
            # Семантическая сегментация подгтовленного изображения
            tools.semantic_segmentation(project, segmentation_net)
            # Подсчет треков в кластерах
            tools.counter(project, counter_net)

    @staticmethod
    def findSame(path):
        '''Поиск смежного файла на основе имени исходного'''
        dir = os.path.dirname(path)
        main_file=os.path.basename(path)
        main_file_name, main_file_end = main_file.split('.')
        files = []
        cut = -1
        while len(files)<2:
            cut+=1
            files = []
            check = main_file_name[:len(main_file_name)-cut]
            for filename in sorted(os.listdir(dir)):
                if check in filename.split('.')[0]:
                    files.append(os.path.normpath(os.path.join(dir,filename)))
        return files

    @staticmethod
    def commonString(string1, string2):
        '''Выделение общей части из двух строк'''
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
        '''Чтение изображения из файла с переводом из BGR в RGB'''
        img = cv2.imread(path)
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    @staticmethod
    def binnary2rgb(img:np.ndarray):
        '''Создание псевдо-RGB из бинарного одномерного массива'''
        img = np.argmax(img, axis=2)*255
        img = np.concatenate([img[...,None],img[...,None],img[...,None]], axis=2).astype(np.uint8)
        return img

    @staticmethod
    def filtBinnary(data, threshold):
        '''Генерализация бинарного изображения'''
        ret, thresh = cv2.threshold(data, threshold, 1, cv2.THRESH_BINARY)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (20, 20))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        return thresh

    @staticmethod
    def getContours(binimg):
        '''Получение контуров из бинарного изображения'''
        contours, hierarchy = cv2.findContours(binimg.copy(), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=lambda ctr: cv2.boundingRect(ctr)[1])
        return contours, hierarchy

    @staticmethod
    def calc_params(contour):
        '''Инструмент вычисления основных параметров выделенного кластера'''
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

        # заполнение шаблон слепка в пределах контура (остальное 0)
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
        '''Посдсчет треков на изображении и заполнение проекта'''
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