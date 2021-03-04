import cv2

def _match(img, template, method):
    '''Search for an area in an image
    
    Return: Coords of rectangle and value of similarity
    '''
    # Creation matrix of results
    res = cv2.matchTemplate(img, template, method)
    
    # Search rectangle
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    # TOP LEFT point
    if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
        top_left = min_loc ; value = min_val
    else:
        top_left = max_loc ; value = max_val
    # BOTTON RIGHT point
    w, h = template.shape[::-1]
    bottom_right = (top_left[0] + w, top_left[1] + h)

    return top_left, bottom_right, value


def detected(img, template, method='TM_CCOEFF'):
    '''
    Function for detection template on img using 'Template Matching'.

    methods: 
    - 'TM_CCOEFF', 'TM_CCOEFF_NORMED'
    - 'TM_CCORR', 'TM_CCORR_NORMED'
    - 'TM_SQDIFF', 'TM_SQDIFF_NORMED'
    '''
    method = eval(f'cv2.{method}')

    top_left, bottom_right, value = _match(img, template, method)

    return top_left, bottom_right
