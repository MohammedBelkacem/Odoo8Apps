class parent:

    def __init__(self, param):

        self.v1 = param



class child(parent):

    def __init__(self, param):

        self.v2 = param



obj = child(11)

print ("%d %d" % (obj.v1, obj.v2))