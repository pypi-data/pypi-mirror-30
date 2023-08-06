import maya.cmds as mc

dictionaries = [0] * 2
texts = []
#print(originalMatrix)

win = mc.window(title = "Attribute Checker")#, wh=(158,512))

col = mc.columnLayout(adjustableColumn=True)
nodeTextField = mc.textField(alwaysInvokeEnterCommandOnReturn=True, text="Node Name")
mc.rowLayout(numberOfColumns=2, columnAlign=[(1, "center"),(2,"center")])
mc.columnLayout()
mc.button(label="Set Original", command="setMatrix(dictionaries, 0)")
texts.append(mc.text(label="Set: No", align="center"))
mc.setParent("..")
mc.columnLayout()
mc.button(label="Set Changed", command="setMatrix(dictionaries, 1)")
texts.append(mc.text(label="Set: No", align="center"))
mc.setParent("..")
mc.setParent("..")
mc.separator()
readyText = mc.text(label="Is Ready: No", align="center")
mc.button(label="Compare Changes", command="compareChanges(dictionaries)")

mc.showWindow(win)

def setMatrix(dictionaries, num):
    nodeText = mc.textField(nodeTextField, query=True, text=True)
    #print(mc.listAttr(nodeText))
    tempDictionary = {}
    for i in mc.listAttr(nodeText):
        #print(i)
        try:
            tempDictionary[i] = (
                mc.getAttr("%s.%s"%(nodeText, i), silent=True, asString=True), 
                mc.getAttr("%s.%s"%(nodeText, i), silent=True, asString=True, type=True),
                mc.getAttr("%s.%s"%(nodeText, i), silent=True))
        except (RuntimeError, ValueError) as e:
            tempDictionary[i] = ("FAILED","NONE","FAILED")
    #print(tempDictionary)        
    
    dictionaries[num] = tempDictionary
    mc.text(texts[num], edit=True, label="Set: Yes")
    
    if dictionaries[0] != 0 and dictionaries[1] != 0:
        mc.text(readyText, edit=True, label="Is Ready: Yes")
        
class compareChanges():

    titles = ["Attribute Name","Original Value","Changed Value","Value Type","Get Real Value"]
    commands = [
        "key", 
        "self.dictionaries[0][key][0]", 
        "self.dictionaries[1][key][0]", 
        "self.dictionaries[1][key][1]"]
    comparisons = {}
        
    def __init__(self, dictionaries):
        self.dictionaries = dictionaries
        
        win = mc.window(title="Attribute Comparison", resizeToFitChildren=True)
        columns = len(self.titles)
        mc.columnLayout(adj=True)
        #mc.frameLayout(label="String values", collapsable=True)
        mc.scrollLayout()
        col = mc.rowLayout(numberOfColumns=columns)
        for i in range(columns):
            self.createColumn(i)
        #mc.frameLayout(label="Real values", collapsable=True)
    
        # Can add a list of only changed items

        mc.showWindow(win)
        
    def informationWindow(self, key):
        win = mc.window(title="Attribute Information")
        mc.columnLayout(adj=1)
        mc.rowLayout(numberOfColumns=2)
        exec("name="+self.commands[0]) in locals(), globals()
        print(key)
        mc.textFieldGrp(label="Name", text=name, enable=False)
        #exec("nameType="+self.commands[1]) in locals(), globals()
        #print(type)
        #mc.textFieldGrp(label="Type", text=nameType, enable=False)#self.dictionaries[1][key][1]
        
        mc.showWindow(win)
        
    def handleCommand(self, i):
        keys = self.dictionaries[0].keys()
        for key in keys:
            if i != 4:
                check = False
                exec("tempString = str(%s)"%self.commands[i]) in locals(), globals()
                if i == 1:
                    self.comparisons[key] = tempString
                elif i == 2:
                    if self.comparisons[key] != tempString:
                        check = True
                tempText = mc.text(label=tempString[:35], height=15)  
                if check:
                    mc.text(tempText, edit=True, font="boldLabelFont", backgroundColor=(1,0.5,0.5))
            else:
                mc.button(label="Real Value", height=15, command=lambda key : self.informationWindow(key))#informationWindow(key)")#"print(%s)"%dictionaries[1][key][2], height=15)
        
    def createColumn(self, i):
        mc.columnLayout()
        mc.text(label=self.titles[i], font="boldLabelFont")
        mc.separator(height=5, style="in")
        self.handleCommand(i)
        mc.setParent("..")
        
            

    
    
    