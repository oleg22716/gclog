class Grp:
    def __init__(self, sets):
        self.n_of_sets = sets  # Number of datasets
        self.data = []
        for i in range(0, sets):
            self.data.append([])

    def put(self, *args):
        if len(args) != self.n_of_sets:
            raise ValueError(
                "You have entered " + len(args).__str__() + ", please, put " + self.n_of_sets.__str__() + " here.")
        for i in range(0, self.n_of_sets):
            self.data[i].append(args[i])

    def print(self, number=-1):
        if number == -1:
            print(self.data)
        else:
            print(self.data[number])
