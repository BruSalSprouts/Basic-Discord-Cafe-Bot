class item:
    name = ''
    price = 0
    picturePath = ''

    def __init__(self, name, price, picturePath): #Constructor for item class
        self.name = name
        self.price = price
        self.picturePath = picturePath

    #Getter and Setter for name
    def getname(self):
        return self.name
    def setNewName(self, newName):
        self.name = newName

    #Getter and Setter for price
    def getPrice(self):
        return self.price
    def setNewPrice(self, newPrice):
        self.price = newPrice

    #Getter and Setter for picturePath
    def getPicturePath(self):
        return self.picturePath
    def setPicturePath(self, newPath):
        self.picturePath = newPath