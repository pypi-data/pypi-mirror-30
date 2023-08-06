class WowClass:

    def __init__(self, classname, classid, classspecs):
        self.name = classname
        self.id = classid
        self.specs = self.parsespecs(classspecs)

    def __str__(self):
        return "(ID: " + str(self.id) + ") " + self.name + ''.join("\n\t" + str(spec) for spec in self.specs)

    def parsespecs(self, specs):
        return [Spec(spec["name"], spec["id"]) for spec in specs]


class Spec:

    def __init__(self, specname, specid):
        self.name = specname
        self.id = specid

    def __str__(self):
        return "(ID: " + str(self.id) + ") " + self.name
