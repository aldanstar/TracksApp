import numpy as np
from enum import Enum
from typing import Dict,List
from app.tools import tools

# Перечисление типов элементов конструкции
class ElementType(Enum):
    UNDEFINED = 0

    PROJECT = 1

    SAMPLES = 2
    SAMPLE = 3

    UTRACKS = 4
    UTRACK = 5

# Базовый класс элемента конструкции скважины
class BaseProjectElement:
    """ Базовый класс элемента конструкции скважины """
    __slots__ = (
    'type', 'name', 'hint', 'tag', 'number', 'top', 'bottom', 'top_prj', 'bottom_prj', 'id', 'parent', 'root')

    def __init__(self):
        self.type: ElementType = ElementType.UNDEFINED  # тип элемента - не определен: ElementType.UNDEFINED = 0
        self.name = ''  # имя элемента конструкции скважины
        self.hint = ''  # подсказка
        self.tag = 0  # целевая ссылка (используется по месту)
        self.number = 0  # прорядковый номер элемента
        self.top = None  # 'верх'
        self.bottom = None  # 'низ'
        self.top_prj = 0  # проектный 'верх'
        self.bottom_prj = 0  # проектный 'низ'
        self.id = None
        self.parent = None
        self.root = None

    def delete(self):
        self.parent.delete_item(self)


class ParentProjectElement(BaseProjectElement):
    """ Базовый класс элемента конструкции скважины """
    __slots__ = ('__CID__', 'items')

    def __init__(self):
        super().__init__()
        self.__CID__ = 0
        self.items = dict()

    def add_item(self, *args):
        self.__add_child__(*args)
        self.__CID__ += 1
        return self.items[self.__CID__-1]

    def __add_child__(self):
        pass

    def overlap(self, start1, end1, start2, end2):
        return (
                start1 <= start2 <= end1 or
                start1 <= end2 <= end1 or
                start2 <= start1 <= end2 or
                start2 <= end1 <= end2
        )

    def delete_item(self, obj):
        if isinstance(obj, (UTrack)):
            self.items.pop(obj.id)
        elif isinstance(obj, int):
            self.items.pop(obj)

    def clear(self):
        self.items.clear()

    def get_count(self):
        return len(self.items)

    def get_items(self):
        return list(self.items.values())

    def get_sorted(self, y_ranges: list([]) = None):
        if y_ranges:
            items = []
            for item in sorted(list(self.items.values()), key=lambda k: k.top):
                if any(self.overlap(item.top, item.bottom, lower, upper) for (lower, upper) in y_ranges):
                    items.append(item)
            return items
        else:
            return sorted(list(self.items.values()), key=lambda k: k.top)

    def get_sorted_by_id(self):

        items = sorted(list(self.items.values()), key=lambda k: k.id)

        return items

# класс трека
class UTrack(BaseProjectElement):
    """ класс параметров трека  """

    def __init__(self, ID=None, parent=None, root=None, left:int=0, rigth:int=0, top:int=0,bottom:int=0, frame:np.ndarray=np.array([]),contour:np.ndarray=np.array([]), area:float=0):
        super().__init__()
        self.id=ID
        self.parent=parent                                  # владелец
        self.root=root
        self.set_params(left, rigth, top, bottom, frame, contour, area)

    def set_params(self, left, rigth, top, bottom, frame, contour, area):
        self.left = left
        self.rigth=rigth
        self.top = top
        self.bottom=bottom
        self.frame=frame.copy()             # двумерный образ
        self.contour=contour
        self.area = area

        self.count = 0


# класс коллекции параметров треков
class UTrackList(ParentProjectElement):

    def __init__(self):
        super().__init__()
        self.type = ElementType.UTRACKS  # тип элемента
        self.items: Dict(UTrack) = {}  # список треков

    """ добавление трека """
    def __add_child__(self, left:int=0, rigth:int=0, top:int=0,bottom:int=0, frame:np.ndarray=np.array([]),contour:np.ndarray=np.array([]), area:float=0):
        self.items[self.__CID__]=UTrack(self.__CID__,self,self.root, left, rigth, top, bottom, frame, contour, area)


# класс образца
class Sample(BaseProjectElement):
    """ класс параметров образца  """

    def __init__(self, ID=None, parent=None, root=None, name:str='noname',  through:np.ndarray=np.array([]),backlight:np.ndarray=np.array([])):
        super().__init__()
        self.id=ID
        self.parent=parent                                  # владелец
        self.root=root
        self.set_params(name, through, backlight)

    def set_params(self, name, through, backlight):
        self.name = name
        self.through = through
        self.backlight = backlight
        self.prepared: np.ndarray = np.array([])

        self.tracks: UTrackList = UTrackList()  # список треков образца
        self.combine_calc()


    def combine_calc(self):
        '''основная процедура создания композиции'''
        img3=tools.mean_bet_imgs(self.through,self.backlight)
        img1=tools.norm_l_extract(self.through)
        img2=tools.norm_l_extract(self.backlight)
        self.prepared=np.dstack((img2,img3,img1))

# класс коллекции параметров треков
class Samples(ParentProjectElement):

    def __init__(self, root=None):
        super().__init__()
        self.root = root
        self.parent = root
        self.type = ElementType.SAMPLES  # тип элемента
        self.items: Dict(Sample) = {}  # список треков

    """ добавление образца """
    def __add_child__(self, name:str='noname', through:np.ndarray=np.array([]),backlight:np.ndarray=np.array([])):
        self.items[self.__CID__]=Sample(self.__CID__,self,self.root, name, through, backlight)
        self.parent.current_sample = self.items[self.__CID__]
        return self.items[self.__CID__]

# Класс проекта
class Project(BaseProjectElement):
    __slots__ = ('samples', 'current_sample', 'name')
    """ инициализация """

    def __init__(self, name=''):
        BaseProjectElement.__init__(self)
        self.name=name
        self.type = ElementType.PROJECT  # тип элемента
        self.samples: Samples = Samples(self)
        self.current_sample = None

    def get_samples_names(self)->List:
        return [sample.name for sample in self.samples.get_sorted_by_id()]
