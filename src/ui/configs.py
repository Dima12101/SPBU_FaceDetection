DATA_DIR = './data'

ALL_METHODS = [
    'TM_CCOEFF', 'TM_CCOEFF_NORMED',
    'TM_CCORR', 'TM_CCORR_NORMED',
    'TM_SQDIFF', 'TM_SQDIFF_NORMED']

ALL_DATABASES = ['ORL', 'Yale_faces']

DATABASE_CONF = {
    'ORL': {
        'number_group': 40,
        'number_img': 10,
        'img_path': './data/ORL/s{g}/{im}.pgm'
    },
    'Yale_faces': {
        'number_group': 15,
        'number_img': 11,
        'img_path': './data/Yale_faces/subject{g}.*'
    },
}

IMG_PATH_F = './data/s{g}/{im}.pgm'