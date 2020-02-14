# Read and Process Input Files

class File:

    def __init__(self, filename):
        self.fileName = filename
        self.graph = []
        self.homes = []

    '''
        Extract graph from input file
        Replace all 'x' with 0
        Generate list of home indices
    '''
    def readFile(self):
        # read file, change every x to 0, save to graph
        count = 0
        location_names = []
        home_names = []
        with open(self.fileName, 'r') as f:
            for i in f:
                count += 1
                if count == 3:
                    location_names = i.split(" ")[:-1]
                elif count == 4:
                    home_names = i.split(" ")[:-1]
                elif count >= 6:
                    s = i.split(" ")[:-1]
                    for j in range(len(s)):
                        if s[j] == 'x':
                            s[j] = 0
                        s[j] = float(s[j])
                    self.graph.append(s)

        # save home indices
        for i in range(len(location_names)):
            if location_names[i] in home_names:
                self.homes.append(i)

    def getGraph(self):
        return self.graph

    def getHomes(self):
        return self.homes