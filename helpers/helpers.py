
def get_int(num):
    try:
        num = int(num)
    except:
        num = 0

    return num


def length(elem):
    try:
        l = len(elem)
    except:
        l = 0
    return l
