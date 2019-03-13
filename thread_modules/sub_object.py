# Sub sysObject grouping type
# module type: def
import object

# objects can be like groups without being groups
# parent and child objects have a "sub" section in their thread_modules

# "sub": {"parent": [reference, offset], "children": [reference, ...]}

# reference:objId
# offset: is the distance of the  parent's position to the sysObject's position in the format [x,y,z]
# if an sysObject has one child put it in a list by its self
# if a sysObject has no children but a prent leave "children" set to an empty list ([])
# if a sysObject has no parent set "parent" to None
# if an sysObject has neither children or a parent remove the "sub" entry or set it to None
# children's move becomes child.mov = "sub"

# ex parent: "sub": {"parent": None, "children": [child0]}
# ex child: "sub": {"parent": [parent0, [1,1,1]], "children":[child1]}


# Sub sysObject
# parent([objId(str), [x,y,z]]/None), children([obj]/[])
class sub:
    def __init__(self, parent=None, children=None):
        self.parent = parent
        if children is None:
            self.children = []
        else:
            self.children = children

    # sets parent
    # parent(obId(str)), offset([x,y,z])
    # none
    def setParent(self, parent, offset):
        self.parent = [parent, offset]

    # set children
    # children([child(objId(str))])
    # none
    def setChildren(self, children):
        self.children = children

    # add a child to a parent
    # child(objId(str))
    # none
    def addChild(self, child):
        self.children.append(child)

    # remove child rom parent
    # index(int)
    # none
    def removeChild(self, index):
        self.children.pop(index)

    # pack data for ram
    # none
    # dta(sub attribs, tags)
    def package(self):
        return object.data([self.parent, self.children], {"name": "tread.sub.package", "id": None,
                                                          "dataType": "thread.sub.package"})


# Info at run
if __name__ == "__main__":
    print("Sub sysObject grouping type\nmodule type: def")
