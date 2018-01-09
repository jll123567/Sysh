# setup

# model stores any sort of model of the object
# accepts png, stl, and the method below
#
#   Model format=[[scale,"x,y,z-x,y,z","..."],[scale,["x,y,z",["x,y,z","..."],["x,y,z","..."]],[that,all,again]],[scale,[[["original skpos","new pos","next"],[data for next point]],[next animation]]],[texture,[physx properties]]]
#   assem [[scale,["x,y,z,p,ya,r",obj] and material = "assem"


def makeModel(model, obj, material):
    obj.mod[0] = model
    obj.mod[3] = material
    return obj
#    else:
#        points=[[]]
#        working=True
#        while working:
#            if points=[[]]:
#                points.insert(0,input("scale from a(1mm=100000000a so 100000000)"))
#            x1=0
#            y1=0
#            z1=0
#            print("first point of new edge from origin")
#            x1=input("x:")
#            y1=input("y:")
#            z1=input("z:")
#            x2=0
#            y2=0
#            z2=0
#            print("second point of new edge from origin")
#            x2=input("x:")
#            y2=input("y:")
#            z2=input("z:")
#            points[1].append(str(str(x1)+","+str(y1)+","+str(z1)+"-"str(x2)+","str(y2)+","str(z2))
#            check=input("are you done(y/n)")
#            if check="y":
#                working=False
#        object.mod[0]=points


def rigModel(rigging, obj):
    obj.mod[1] = rigging
    return obj


def setAnimations(obj, ani):
    obj.mod[2] = ani
    return obj


def addAnimation(animation, obj):
    obj.mod[2].append(animation)
    return obj


def displaySysModel(obj):
    for f in obj.mod[0]:
        if isinstance(f, list):
            displaySysModel(f[1])
            print("@" + f[0])
        elif isinstance(f, str):
            print("scale:" + f + "a for each unit")
        else:
            print(f)
    for i in obj.mod[1]:
        print(i[0])
        for f in i[1]:
            print(f)
        for f in i[2]:
            print(f)
    print(obj.mod[2][0], "frames per second")
    for i in obj.mod[2][1]:
        print(i)
    print("material:", obj.mod[3])


def newAssem(obj, assem, ani, rig):
    obj.mod[0] = assem
    obj.mod[1] = rig
    obj.mod[2] = ani
    obj.mod[3] = "assem"
    return obj

    # open("filename","mode")


def imgAsModel(obj, file):
    obj.mod = file
    return obj


def stlAsModel(obj, file):
    obj.mod = file
    return obj


# runtime
if __name__ == "__main__":
    print("model rigging v10.0")
