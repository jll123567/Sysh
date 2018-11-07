# coding=utf-8
# object type definitions
# module type: def
from random import randint
import attribs
from math import sqrt
import error
import prog.idGen


# sysh.object.object(oof better name pls) model of object(any), relevant self viewable data(attrib's.thread.trd),
# tags and data for system/admin({tag:(str),...}) noinspection PyShadowingBuiltins
class object:
    def __init__(self, mod=attribs.model.sysModel(), trd=attribs.thread.trd(), tag=None):
        self.mod = mod
        self.trd = trd
        if tag is None:
            self.tag = {"id": None, "name": None}
        else:
            self.tag = tag

    # make an object's model dependant of sub objects
    # none
    # none
    def makeModelAssembly(self):
        oldModel = self.mod
        # noinspection PyTypeChecker
        self.tag.update({"oldModel": oldModel})
        self.mod = "assem"

    # damages the internal of obj (mem type only on usr)
    # wep(wep)*
    # none/ Console Output(str)
    def internalDamage(self, wep):
        for i in wep.dmg.damages:
            if i[1] == "mem":
                if isinstance(self, user):
                    self.mem.real.pop(randint(0, self.mem.real.len()))

            elif "trd" == i[1]:
                self.trd.tsk.current = None
            else:
                print("unsupported")

    # modifies the value of <stat>
    # wep(wep)*, dmgIndex(int)*
    # none/ Console Output(str)
    def statDamage(self, wep, dmgIndex):
        for key in self.tag["stat"].keys():
            if key == wep.dmg.damages[dmgIndex][1]:
                self.tag["stat"][key] -= wep.dmg[dmgIndex][0]
            else:
                print("obj does not have the stat ", wep.dmg[dmgIndex][1], " \nDid you misspell it?")

    # remove health based on atk
    # wep(wep)*
    # none
    def attack(self, wep):
        for i in wep.dmg.damages:
            if i[1] == "health":
                self.tag["health"] -= i[0]

    # asks some questions to check if obj is a usr
    # console input
    # console output/ obj/ usr
    def usershipQuery(self):
        print("can get info from and modify $HostUni")
        rww = input("y/n")
        print("can get and store objects in memory")
        rwi = input("y/n")
        print("attempts to add reason to previous current and future actions")
        rea = input("y/n")
        print("can add new functions to tasker")
        lrn = input("y/n")
        print("attempts to reserve or increase the integrity and freewill of objects or users")
        mor = input("y/n")
        print("does not == another obj")
        unq = input("y/n")
        total = [rww, rwi, rea, lrn, unq, mor]
        fail = False
        for i in total:
            if i != 'y' or i != 'n':
                fail = True
                print("form incorrectly filled")
                break
            if i == 'n':
                fail = True
                if isinstance(self, user):
                    oldUsrDta = [self.prs, self.mem]
                    objActual = object(self.mod, self.trd, self.tag)
                    # noinspection PyTypeChecker
                    self.tag.update({"oldUsrDta": oldUsrDta})
                    print(self.tag["name"], "is Now Object")
                    return objActual
                else:
                    print(self.tag["name"], "is Object")
        if not fail:
            if isinstance(self, object):
                usr = user(self.mod, self.trd, self.tag["notes"][0], self.tag["notes"][1], self.tag)
                print(self.tag["name"], "is Now User")
                return usr
            else:
                print(self.tag["name"], "is User")

    # remove a parent from a child obj
    # parent(obj)*
    # none
    def removeParent(self, parent):
        parentMov = [parent.trd.mov.x, parent.trd.mov.y, parent.trd.mov.z, parent.trd.mov.a, parent.trd.mov.b,
                     parent.trd.mov.c]
        offset = self.trd.sub.parent[1]
        self.trd.mov.x = parentMov[0] + offset[0]
        self.trd.mov.y = parentMov[1] + offset[1]
        self.trd.mov.z = parentMov[2] + offset[2]
        self.trd.mov.a = parentMov[3]
        self.trd.mov.b = parentMov[4]
        self.trd.mov.c = parentMov[5]
        self.trd.sub.parent = None


# sysh.object.user
# model(any), thread(thread.trd), prs(personality.prs), memory(memory.mem) tag({"id":(str), ...})
class user(object):
    def __init__(self, mod=attribs.model.sysModel(), trd=attribs.thread.trd(), prs=attribs.personality.prs(),
                 mem=attribs.memory.mem(), tag=None):
        self.mod = mod
        if tag is None:
            self.tag = {"id": None, "name": None, "alias": []}
        else:
            self.tag = tag
        self.trd = trd
        self.prs = prs
        # working on it
        self.mem = mem

    # saves a copy of ram ro memory
    # storedRamName(str)*, storedRamImportance(int[0-100])*
    # none
    def storeToMemory(self, storedRamName, storedRamImportance):
        dta = data([self.trd.ram.storage],
                   {"id": None, "name": storedRamName, "relevancy": [0, 0, storedRamImportance]})
        dta.tag["id"] = prog.idGen.generateGenericId(self.mem.real, dta)
        self.mem.store(1, dta)

    # load a mem obj to ram
    # block(int[0-2])*, index(int)
    # none
    def loadToRam(self, block, index):
        if block == 0:
            print("no internal access")
        elif block == 1:
            self.trd.ram.load(self.mem.real[index])
        else:
            self.trd.ram.load(self.mem.external[index])

    # check the integrity of an object
    # past of obj(obj)*, obj now(obj)*
    # status(str)
    @staticmethod
    def checkIteg(objPast, objCurrent):
        if objPast.tag["health"] > objCurrent.tag["health"]:
            return "reduced"
        else:
            return "maintained"

    # check freedom of will(functions available)
    # past of obj(obj)*, obj now(obj)*
    # status(str)
    @staticmethod
    def checkWill(objPast, objCurrent):
        if objPast.tag["functlist"].__len__() > objCurrent.tag["functlist"].__len__():
            return "reduced"
        else:
            return "maintained"

    # get the relevancy of an object
    # obj(obj)*
    # relevancy(int)
    @staticmethod
    def calculate_relevancy(obj):
        if obj.tag["relevancy"][1] == 0:
            return 100 + (sqrt(obj.tag["relevancy"][1]) * 10) + 25 + (obj.tag["relevancy"][2])
        else:
            return (100 * ((1 / 3) ** obj.tag["relevancy"][0])) + (sqrt(obj.tag["relevancy"][1]) * 10) + (
                obj.tag["relevancy"][2])

    # load a queue from real memory
    # real index(int)*
    # none
    def loadQueue(self, realIndex):
        self.trd.que = self.mem.real[realIndex].storage

    # save a queue to real mem
    # tags(tag)*
    # none
    def saveQueue(self, tags):
        lastQueue = data(self.trd.que, tags)
        self.mem.store(1, lastQueue)
        print("queue saved to: ", lastQueue, "@", self.tag["id"], ".mem.real")


# weapons
# mod(any), thread(thread.trd), damage profile(damage.dmg), tag({"id":(str), ...})
class weapon(object):
    def __init__(self, mod=attribs.model.sysModel(), trd=attribs.thread.trd(),
                 dmg=attribs.damage.dmg(), tag=None):
        self.mod = mod
        if tag is None:
            self.tag = {"id": None, "name": None}
        else:
            self.tag = tag
        self.trd = trd
        self.dmg = dmg


# packaged data
# storage(any), tag({"id":(str), ...})
class data:
    def __init__(self, storage=None, tag=None):
        if tag is None:
            self.tag = {"id": None, "name": None}
        else:
            self.tag = tag
        self.storage = storage


# spaces
# origin in relation to supercont([supercont,x,y,z]), bounds[["h/s,x,y,z-x,y,z"], ...], tag({"id":(str), ...})
class container:
    def __init__(self, org=None, bnd=None, tag=None):
        if org is None:
            self.org = [None, 0, 0, 0]
        else:
            self.org = org
        if bnd is None:
            self.bnd = [["h,0,0,0-0,0,0"]]
        else:
            self.bnd = bnd
        # [“(h/s,)x,y,z-x,y,z”,...]
        # [None] means no bounds
        if tag is None:
            self.tag = {"id": None, "name": None}
        else:
            self.tag = tag


# object change oer time
# scp([tlInfo, shft0, shft1, ...]), obj in scene([obj]), loc(container), tag({"id":(str), ...})
class scene:
    def __init__(self, scp=None, obj=None,
                 cont=container([None, 0, 0, 0], ["h,0,0,0-0,0,0"],
                                {"id": None, "name": "defaultContainer"}), tag=None):
        if scp is None:
            self.scp = [["master", None, 30]]
        else:
            self.scp = scp
        # [time([tl branch, start point, shift per sec]),command0,command1,...]
        # if timeline start point is none then is "unploted"
        if obj is None:
            self.obj = []
        else:
            self.obj = obj
        # objlist
        self.cont = cont
        # cont
        # use a super cont that will contain all relevant containers
        if tag is None:
            self.tag = {"id": None, "name": None}
        else:
            self.tag = tag

    # unplot the scene from a uni time line
    # none
    # none
    def unplotTl(self):
        self.scp[0] = ["master", None, 30]

    # add an error to the scene
    # objListIdx(int)*, type(int[0-2])*, sev(int[0-])*, mes(str)*, res([str])*, sel(int)
    # none
    def raiseError(self, objListIdx, errType, sev, mes, res, sel):
        e = error.err(errType, sev, mes, res, sel, self.obj[objListIdx], self.cont, {"id": ""})
        e.tag["id"] = prog.idGen.generateGenericId(self.obj, e)
        self.obj.append(e)

    # add a request to the scene
    # request(str)*, index for requester in scn.obj(int)*
    # none
    def raiseRequest(self, request, objListIdx):
        d = data([request, self.cont, self.obj[objListIdx]], {"id": "", "dataType": "request"})
        d.tag["id"] = prog.idGen.generateGenericId(self.obj, d)
        self.obj.append(d)


# scene container timeline(time line info), scn([scn]), obj([obj]), cont([cont]), funct([functions]),
# rule([operations to run on all obj each shift]), tag({"id":(str), ...})
class universe:
    def __init__(self, tl=None, scn=None, obj=None, cont=None, funct=None, rule=None, tag=None):
        if tl is None:
            self.tl = attribs.timeLine.timeline()
        else:
            self.tl = tl
        if scn is None:
            self.scn = []
        else:
            self.scn = scn
        # scene list in or
        # der like(0,0)(0,1)(1,0)(1,1)
        if obj is None:
            self.obj = []
        else:
            self.obj = obj
        # objlist
        # [usr, wep, obj, dta]
        if cont is None:
            self.cont = []
        else:
            self.cont = cont
        # container struct
        if funct is None:
            self.funct = []
        else:
            self.funct = funct
        # functions unique to uni
        if rule is None:
            self.rule = []
        else:
            self.rule = rule
            # a rule is an operation run at each object
            # [extension(optional. None for no ext), function, [parameters]]
        if tag is None:
            self.tag = {"id": None, "name": None}
        else:
            self.tag = tag


# info at run
if __name__ == "__main__":
    print("object type definitions\nmodule type: def")
