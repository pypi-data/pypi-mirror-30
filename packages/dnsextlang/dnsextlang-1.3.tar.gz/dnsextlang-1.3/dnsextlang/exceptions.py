# extrec exceptions
# python3 only
# version 1.0

class ExtSyntax(Exception):
    " bad record syntax "
    def __init__(self, msg):
        self.msg = msg

class ExtKeytype(Exception):
    " bad types in fetch or append "
    pass

class ExtBadField(Exception):
    "unknown extlang field type"
    def __init__(self, msg):
        self.msg = "Unknown field type "+msg

class ExtUnimp(Exception):
    "unimplemented extlang field method"
    def __init__(self, msg):
        self.msg = msg

