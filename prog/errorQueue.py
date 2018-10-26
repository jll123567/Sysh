# a small bug tracker like thing
# module type: prog
import error
import object
import prog.idGen

# error queue(fill with err)
errQueue = []
requestQueue = []
inProgress = {}
cases = []


# queues and resolves a list of errors
# errs([err])*
# Console output(str)
def errorResolve(userId=None):
    global inProgress, errQueue
    idx = 0
    if userId is None:
        for errs in errQueue:
            errs.resolveError()
            errQueue = []
        print("queue completed closing")
    else:
        for errs in inProgress[userId]:
            errs.resolveError()
            inProgress[userId].pop(idx)
            idx += 1
        print("queue completed, closing")


# populate the queue
# uni(uni)*, mode('e', 'r')
# none
def populateQueue(scn, mode='e'):
    global errQueue, requestQueue
    if mode == 'e':
        for scn in scn.scn:
            for obj in scn:
                if isinstance(obj, error.err):
                    errQueue.append(obj)
    else:
        for scn in scn.scn:
            for obj in scn:
                try:
                    if obj.tag["dataType"] == "request":
                        requestQueue.append(obj)
                except AttributeError:
                    noTagAtObject(obj)
                except KeyError:
                    pass


#
#
#
def assign(userId, idxList, mode='e'):
    global inProgress, errQueue, requestQueue
    if mode == 'e':
        errList = []
        for idx in idxList:
            errList.append(errQueue[idx])
            errQueue.pop(idx)
    else:
        errList = []
        for idx in idxList:
            errList.append(requestQueue[idx])
            requestQueue.pop(idx)
    inProgress.update({userId: errList})


#
#
#
def caseFileCompiler(userId, userName, desc, packages=None):
    global cases
    if packages is None:
        packages = []
    tags = {"dataType": "caseFile", "caseInfo": {"id": prog.idGen.generateCaseId(cases),
                                                 "userInfo": [userId, userName], "description": desc}}
    dta = object.data()
    dta.storage = packages
    dta.tag.update(tags)
    return dta


#
#
#
def closeIssue(userId, idx):
    global inProgress
    inProgress[userId].pop(idx)


#
#
#
class noTagAtObject(Exception):
    def __init__(self, expression, message="the object does not have the required \"tag\" attribute"):
        self.expression = expression
        self.message = message


# info at run
if __name__ == "__main__":
    print("a small bug tracker like thing\nmodule type: prog")
