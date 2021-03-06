"""
Module for session.

Classes
    Session(Thread, Tagable)
"""
from sysObjects.Tagable import Tagable
from sysObjects.Taskable import Taskable
from sysObjects.Data import Data
from sysObjects.Scene import Scene
from sysModules.Tasker import Shift, Operation
import copy
from threading import Thread


class Session(Thread, Tagable):
    """
    An instance of objects that interact with each-other.

    Like a live Universe.

    Attributes
        _ops [Operation]: Operations to execute in current shift.
        _deleteOnEmptyTasker bool: Toggle to remove objects with empty Taskers from objectList.
        _killOnEmptySession bool: Toggle to kill thread if objectList is empty.
        pendRequest bool: Holds weather the Session has been told to pend shifts by directory.
        pended bool: Holds if the Session is currently pending stuff from the directory.
        directory Directory: The Directory that this session is within.
        objectList [Tagable]: The objects in the session.
            Preferably they are all Taskable.
        scene Scene: The scene to save shifts to.
        rules [Operation]: List of operations to run every shift.
        tags dict: Tags.

    Tags
        id str: Session's id.
            Format: "dr/<directory>/un/<universe this session represents>"
        errs [BaseException]: Stores all logged exceptions.
        opLog [tuple]: Stores executed ops.
            Format: (<function>, <target>, <source>)
        permissions [whitelist, blacklist]: List of permissions.

    Methods
        getObjectFromId(str objectId) -> Tagable: Get the object with a matching id tag.
        update(): Preform all the operations of a shift.
        objectOpCollect(): Get operations from objects in objectList.
        ruleOpCollect(): Get operations from rules.
        objectOpCheck(Operation op) -> bool: Check an operation from an object and return True if its good and false if
            its bad.
        fullOpCheck(Operation op) -> bool: Check an operation from an object or rules and return True if its good and
            false if its bad.
        resolve(): Change keywords and ids in Operations to references to the actual objects.
        execute(Operation op): Take an operation and execute the listed function on the target object or objects.
        log(): Save details of what happened this shift to various locations.
        cleanup(): Cleanup the session for the next shift.
        run(): Obligatory run method.
            Called with start().
        addObject(object obj): Tasker callable method to add an object to the session.
        removeObject(object obj): Tasker callable method to remove an object from the session.
        importFromUniverse(Universe universe): Assign <universe> as the session's universe and set the objectList and id
            with <universe>.
        setupSavedScene(Container cont, str/None sceneId=None, list tl=None, dict tags=None): Create and assign a scene
            to log to.
        exportCurrentToUniverse() -> Universe: Take the session's universe and output it.
    """

    def __init__(self, sesId, parentDir=None, obj=None, uni=None, rul=None, tags=None):
        super().__init__()  # Init thread
        self._ops = []
        self.deleteOnEmptyTasker = False
        self.killOnEmptySession = True
        self.pendRequest = False
        self.pended = False
        self.live = True
        if tags is None:
            self.tags = {}
        else:
            self.tags = tags
        if rul is None:
            self.rules = []
        else:
            self.rules = rul
        if obj is None:
            self.objectList = []
        else:
            self.objectList = obj
        self.universe = uni
        self.directory = parentDir
        self.scene = None
        self.tags["id"] = sesId
        self.tags["permissions"] = [
            [  # allowed
                ("all", "getObjectFromId"),
                ("all", "objectOpCheck"),
                ("all", "fullOpCheck"),
                ("all", "fullDiscovery")
            ],
            [  # blocked
                ("all", "all")
            ]
        ]
        self.tags["errs"] = []
        self.tags["opLog"] = []

    def __str__(self):
        aliveOrDead = "Dead"
        if self.live:
            aliveOrDead = "Alive"
        return "{}:{}:objects:{}".format(self.tags["id"], aliveOrDead, self.objectList.__len__())

    def getObjectFromId(self, objId):
        """
        Get the object with a matching id tag.

        :param str objId: The id to match for.
        :return: The object with matching id.
        :rtype: Tagable
        """
        for o in self.objectList:
            try:
                if objId == o.tags["id"]:
                    return o
            except AttributeError:
                # Error for object with no tags.
                # print("{} object found with no tags.".format(type(o)))  # debug
                pass
        return None

    def update(self):
        """Preform all the operations of a shift."""
        self.objectOpCollect()  # get object ops
        for op in self._ops:  # check em all
            if not self.objectOpCheck(op):  # if they are bad make target none.
                op.target = "none"

        self.ruleOpCollect()  # get rule ops
        for op in self._ops:  # checking like before, but for different criteria.
            if not self.fullOpCheck(op):
                op.target = "none"

        self.resolve()  # Replace some things.
        for op in self._ops:
            self.execute(op)  # Call the functions on the objects.
        self.log()  # Log what happened.
        self.cleanup()  # Prepare for next shift.

    def objectOpCollect(self):
        """Get operations from objects in objectList."""
        for o in self.objectList:  # Get all ops from objects.
            if "health" in o.tags.keys() and o.tags["health"] <= 0:  # Skip this object if its health is zero or less.
                continue
            try:
                objShift = o.tasker.__next__()  # Pops shift from o's tasker!
                for op in objShift:  # Pops op from objShift!
                    self._ops.append(op)
            except BaseException as e:
                if not isinstance(e, StopIteration):
                    self.tags["errs"].append(e)  # Log error

    def ruleOpCollect(self):
        """Get operations from rules."""
        for op in self.rules:  # Unlike in objectOpCollect, no popping.
            self._ops.append(op)

    def objectOpCheck(self, op):
        """
        Check an operation from an object and return True if its good and false if its bad.

        This is for ops from objects(so not including rules).

        :param Operation op: The operation to check.
        :return: Operation's validity.
        :rtype: bool
        """
        if op.target == "all":  # all is not a valid target from objects.
            return False
        if not isinstance(op.source, (str, Taskable)):  # ops must have the object that created them as a source.(so
            # a str for id or a Taskable object at least)
            return False

        try:  # Permissions check.
            if isinstance(op.target, Tagable):  # Get target permissions(here if trg is an object).
                perms = op.target.tags["permissions"]

            else:
                if op.target == "ses":  # If target is a str.
                    perms = self.tags["permissions"]  # Session perms for "ses".
                elif op.target == "dir":
                    perms = self.directory.tags["permissions"]  # Directory perms for "dir"
                else:
                    perms = self.getObjectFromId(op.target).tags["permissions"]  # Resolve the object and get its perms.
        except KeyError:  # bb-but what if no permissions tag.
            perms = [[], []]  # Use blank(accept all) perms.
        except BaseException as e:  # bb-but what if other err.
            if not isinstance(e, StopIteration):
                self.tags["errs"].append(e)  # Log error
            perms = [[], []]  # more blank perms. Yeah!
        if isinstance(op.source, Tagable):  # Get source id.
            s = op.source.tags["id"]
        else:
            s = op.source
        f = op.function  # f is a nice var name.
        if not ((s, f) in perms[0] or (s, "all") in perms[0] or ("all", f) in perms[0] or ("all", "all") in perms[0]):
            # No entry in whitelist? Check black list.
            if (s, f) in perms[1] or (s, "all") in perms[1] or ("all", f) in perms[1] or ("all", "all") in perms[1]:
                # Entry in blacklist? Block.
                return False
        return True

    @staticmethod
    def fullOpCheck(op):
        """
        Check an operation from an object or rules and return True if its good and false if its bad.

        This is for after rules are added and acts as a final check for all ops.

        :param Operation op: The operation to check.
        :return: Operation's validity.
        :rtype: bool
        """
        if op.target is None:  # target should never be none. Use "none" as a keyword instead.
            return False
        return True

    def resolve(self):
        """
        Change keywords and ids in Operations to references to the actual objects.

        Please note that due to how this method handles keyword parameters, "\trg", "\src", "\ses", and "\dir" cannot be
        parameters as they will be replaced with "trg", "src", "ses", and "dir" respectively.
        """
        for op in self._ops:
            if op.target == "none":  # Skip ops that wont run.(none is trg)
                continue
            for o in self.objectList:
                try:
                    if op.target == o.tags["id"]:  # Replace the object's id with a reference to the object itself.
                        op.target = o
                    if op.source == o.tags["id"]:
                        op.source = o
                except AttributeError:  # pass if o is not tagable or has no id
                    pass
                except KeyError:
                    pass

            if op.source == "ses":  # Not sure if this resolution is the best idea yet.
                op.source = self
            elif op.source == "dir":
                op.source = self.directory
            if op.target == "ses":
                op.target = self
            elif op.target == "dir":
                op.target = self.directory

            for pIdx in range(op.parameters.__len__()):
                if op.parameters[pIdx] == "trg":  # Replace trg keyword with target.
                    op.parameters[pIdx] = op.target
                elif op.parameters[pIdx] == "src":  # And so on...
                    op.parameters[pIdx] = op.source
                elif op.parameters[pIdx] == "ses":
                    op.parameters[pIdx] = self
                elif op.parameters[pIdx] == "dir":
                    op.parameters[pIdx] = self.directory
                elif op.parameters[pIdx] in ("\\trg", "\\src", "\\ses", "\\dir"):  # Replace escaped versions of
                    # keywords with the intended string.
                    op.parameters[pIdx] = op.parameters[pIdx][1:]

    def execute(self, op):
        """
        Take an operation and execute the listed function on the target object or objects.

        :param Operation op: Operation to use for execution.
        """
        if op.target == "none":  # do nothing for none target
            return
        elif op.target == "all":  # Handle all keyword.
            for o in self.objectList:
                try:
                    if op.parameters:
                        getattr(o, op.function)(*op.parameters)
                    else:
                        getattr(o, op.function)()
                except BaseException as e:  # Handle errors as they come.
                    if not isinstance(e, StopIteration):
                        self.tags["errs"].append(e)  # Log error
        elif op.target == self.directory:
            self.directory.takePost([op.function, op.parameters, self])
        else:
            try:
                if op.parameters:
                    getattr(op.target, op.function)(*op.parameters)
                else:
                    getattr(op.target, op.function)()
            except BaseException as e:  # Handle errors as they come.
                if not isinstance(e, StopIteration):
                    self.tags["errs"].append(e)  # Log error

    def log(self):
        """Save details of what happened this shift to various locations."""
        for op in self._ops:
            if op.target == "none":  # Skip if none
                continue
            if isinstance(op.target, Tagable):  # Grab object id
                trg = op.target.tags['id']
            else:
                trg = op.target  # If not id copy verbatim.
            if isinstance(op.source, Tagable):
                src = op.source.tags['id']
            else:
                src = op.source
            self.tags["opLog"].append((op.function, trg, src))  # Log format (function, target, source).

        if self.scene is not None:  # Log shift to scene.
            opL = self._ops
            for op in self._ops:  # Replace sessions and directories with keywords.
                if op.function == "crossWarp":  # Reformat crossWarp for scene.
                    op.target = "none"
                    opL.append(Operation("removeObject", [op.source], "ses", op.source))  # Remove as equivalent to
                    # crossWarp.
                if op.source == self:
                    op.source = "ses"
                if op.target == self:
                    op.target = self
                for pIdx in range(op.parameters.__len__()):
                    p = op.parameters[pIdx]
                    if p == self:
                        op.parameters[pIdx] = "ses"
                if op.source == self.directory:
                    op.source = "dir"
                if op.target == self.directory:
                    op.target = "dir"
                for pIdx in range(op.parameters.__len__()):
                    p = op.parameters[pIdx]
                    if p == self.directory:
                        op.parameters[pIdx] = "dir"
                if not isinstance(op.source, str):
                    op.source = op.source.tags["id"]
                if not isinstance(op.target, str):
                    op.target = op.target.tags["id"]

            try:
                opL = copy.deepcopy(opL)  # Copy and save ops list.
                sh = Shift(opL)
                self.scene.script.append(sh)
            except BaseException as e:
                if not isinstance(e, StopIteration):
                    self.tags["errs"].append(e)  # Log error

    def cleanup(self):
        """Cleanup the session for the next shift."""
        for o in self.objectList:  # Remove objects with no more shifts.(should this be enable-able/disable-able).
            if not o.tasker.shifts and self.deleteOnEmptyTasker:
                self.objectList.remove(o)
        self._ops = []
        # print("-----------Shift End-----------")  # debug

    def run(self):
        """Obligatory run method; Called with start()."""
        while self.live:
            self.update()

            while self.pendRequest:  # Handle directory pend requests.
                self.pended = True
            self.pended = False

            if not self.objectList and self.killOnEmptySession:
                self.live = False

    def addObject(self, obj):
        """
        Tasker callable method to add an object to the session.

        :param object obj:
        """
        self.objectList.append(obj)

    def removeObject(self, obj):
        """
        Tasker callable method to remove an object from the session.

        :param object obj: object to remove.
        """
        self.objectList.remove(obj)

    def importFromUniverse(self, universe):
        """
        Assign <universe> as the session's universe and set the objectList and id with <universe>.

        :param Universe universe: Universe to import.
        """
        self.universe = universe
        self.tags["id"] = universe.tags["id"]
        self.objectList = universe.objectList

    def setupSavedScene(self, cont, sceneId=None, tl=None, tags=None):
        """
        Create and assign a scene to log to.

        :param Container cont: Scene container.
        :param str/None sceneId: scene's id. Set to None to generate.
        :param list tl: Timeline info for scene. None for default.
        :param dict tags: Tags.
        """
        if sceneId is not None:
            sId = sceneId
        else:
            sId = None
        objs = []
        for o in self.objectList:
            objs.append(copy.deepcopy(o))
        self.scene = Scene(sId, cont, tl, obj=objs, tags=tags)
        if sId is None:
            self.scene.tags["id"] = self.universe.generateId("sn")

    def exportCurrentToUniverse(self):
        """
        Take the session's universe and output it.

        :return: The updated universe.
        :rtype: Universe
        """
        uni = self.universe
        if self.scene is not None:
            uni.sceneList.append(self.scene)
        return uni

    def fullDiscovery(self, requester):
        """
        Pass a list of the id of all objects in the session to the requester.

        The list is in a data object with an id of None.

        :param StaticObject requester: The object the made the request.
        """
        ids = []
        for o in self.objectList:
            ids.append(o.tags["id"])
        d = Data(None, ids)
        d.tags["dataType"] = "fullDiscovery"
        requester.memory.sts.append(d)
