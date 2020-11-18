import os

class resources:

    GREEN_INDICATOR = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images','g.png'))
    GREY_INDICATOR = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images', 'grey.png'))
    RED_INDICATOR = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images', 'r.png'))
    YELLOW_INDICATOR = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images', 'y.png'))

    SEPNN = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'separation_tracks.h5'))
    SEGNN = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'semantic_tracks.h5'))
    CNTNN = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'counter_tracks.h5'))
    SCALER = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'count_scaler.bin'))



