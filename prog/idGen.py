import object


# TODO: make the ID generator dummy
def generateUniversalId(uni, obj):
    genIdPreChk = 0
    for uniObj in uni.obj:
        idFromObj = str(uniObj.tag["id"])
        slashCnt = 0
        idFromObjProcessed = ""
        for character in idFromObj:
            if slashCnt == 2:
                idFromObjProcessed += character
            if character == '/':
                slashCnt += 1
        idFromObjProcessed = int(idFromObjProcessed[:-1])
        if idFromObjProcessed >= genIdPreChk:
            genIdPreChk = idFromObjProcessed + 1
    chkSumRes = genIdPreChk % 9
    if isinstance(obj, object.object):
        objTypeLetter = 'o'
    elif isinstance(obj, object.user):
        objTypeLetter = 'u'
    elif isinstance(obj, object.weapon):
        objTypeLetter = 'w'
    elif isinstance(obj, object.data):
        objTypeLetter = 'd'
    elif isinstance(obj, object.container):
        objTypeLetter = 'c'
    elif isinstance(obj, object.scene):
        objTypeLetter = 's'
    elif isinstance(obj, object.universe):
        objTypeLetter = 'un'
    else:
        objTypeLetter = 'o'
    genId = uni.tag["name"] + '/' + objTypeLetter + "/" + str(genIdPreChk) + str(chkSumRes)
    return genId

def generateGenericId(objList, obj):
    genIdPreChk = 0
    for listObj in objList:
        idFromObj = str(listObj.tag["id"])
        slashCnt = 0
        idFromObjProcessed = ""
        for character in idFromObj:
            if slashCnt == 1:
                idFromObjProcessed += character
            if character == '/':
                slashCnt += 1
        idFromObjProcessed = int(idFromObjProcessed[:-1])
        if idFromObjProcessed >= genIdPreChk:
            genIdPreChk = idFromObjProcessed + 1
    chkSumRes = genIdPreChk % 9
    if isinstance(obj, object.object):
        objTypeLetter = 'o'
    elif isinstance(obj, object.user):
        objTypeLetter = 'u'
    elif isinstance(obj, object.weapon):
        objTypeLetter = 'w'
    elif isinstance(obj, object.data):
        objTypeLetter = 'd'
    elif isinstance(obj, object.container):
        objTypeLetter = 'c'
    elif isinstance(obj, object.scene):
        objTypeLetter = 's'
    elif isinstance(obj, object.universe):
        objTypeLetter = 'un'
    else:
        objTypeLetter = 'o'
    genId = objTypeLetter + "/" + str(genIdPreChk) + str(chkSumRes)
    return genId


if __name__ == "__main__":
    testList = [object.object(), object.object()]
    testList[0].tag.update({"id": "o/00"})
    testList[1].tag.update({"id": generateGenericId(testList, testList[1])})
