import ast

class CodeVisitor(ast.NodeVisitor): 
    methodName = []
    nodeType = ''
    apiSequence = []
    def __init__(self):
        self.methodName = []
        self.nodeType = ""
        self.apiSequence = []
        self.classInstance = {}

        self.classLevel = -1

        # e.g. temp = A()
        #
        # self.tempClass = A
        self.tempClass = "" 

        # e.g. class A:
        #          def a:
        #              ...
        #
        # self.generalClass = A
        self.generalClass = ""

    def str_node(self, node, level):
        if (level <= self.classLevel):
            self.classLevel = -1
            self.generalClass = ""
        if isinstance(node, ast.AST):
            className = node.__class__.__name__

            fields = [(name, self.str_node(val, level)) for name, val in ast.iter_fields(node) if name not in ('left', 'right')]
            rv = '%s(%s' % (className, ', '.join('%s=%s' % field for field in fields))

            if (self.nodeType == "FunctionDef"):
                if ( className == self.nodeType):
                    fname = fields[0][1]
                    fname = fname[1:-1] # convert "'function'" to "function"
                    self.methodName.append(fname)
            elif (self.nodeType == "Statement"):
                if (className == "Expr"):
                    #print("##########")
                    message = fields[0][1]
                    #print(message)
                    char = message[10]
                    #print(char)
                    if (char == 'N'):
                        message = message[19:]
                        api = ""
                        for i in message:
                            if (i == "'"):
                                break
                            api += i
                        self.apiSequence.append(api)
                        #print(api)
                    if (char == 'A'):
                        message = message[35:]
                        #print(message)
                        instanceName = ""
                        for i in message:
                            if (i =="'"):
                                break
                            instanceName += i
                        message = message[len(instanceName)+22:]
                        #print(message)

                        className = ""
                        if (instanceName == "self"):
                            className = self.generalClass
                        else:
                            className = self.classInstance[instanceName]

                        methodName = ""
                        for i in message:
                            if (i =="'"):
                                break
                            methodName += i
                        self.apiSequence.append(className + "." + methodName)
                        
                    #print(message[10:])
                    #self.apiSequence.append(api)

                elif (className == "Assign"):
                    #print("Assign:")
                    callInfo = fields[1][1]
                    #print(fields)
                    callInfo = callInfo[callInfo.find("id"):]
                    className = ""
                    for char in callInfo[4:]:
                        if (char !="'"):
                            className += char
                        else:
                            break
                    self.apiSequence.append(className)
                    self.tempClass = className
                elif (className == "Name" and self.tempClass != ""): 
                    #print(fields)
                    tempClass = self.tempClass
                    tempInstance = fields[0][1][1:-1]
                    self.tempClass = ""
                    self.classInstance[tempInstance] = tempClass
                    #print(self.classInstance)
                elif (className == "ClassDef"):
                    self.generalClass = fields[0][1][1:-1]
                    self.classLevel = level
                    
            return rv + ')'
        else:
            return repr(node)

    def ast_visit(self, node, level=0):
        message = self.str_node(node, level)
        if (self.nodeType == "print"):
            print('  ' * level + message)
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        self.ast_visit(item, level=level+1)
            elif isinstance(value, ast.AST):
                self.ast_visit(value, level=level+1)

    def visit_print(self, node):
        self.nodeType = "print"
        self.ast_visit(node)

    def visit_MethodName(self, node):
        self.nodeType = "FunctionDef"
        self.ast_visit(node) 
        return self.methodName

    def visit_Statement(self, node): 
        self.nodeType = "Statement"
        self.ast_visit(node) 
        return self.apiSequence

def printAST(code):
    cv = CodeVisitor()
    tree = ast.parse(code)
    cv.visit_print(tree)

def getAPISequence(code):
    cv = CodeVisitor()
    tree = ast.parse(code)
    return cv.visit_Statement(tree)

def getMethodName(code):
    cv = CodeVisitor()
    tree = ast.parse(code)
    return cv.visit_MethodName(tree)
    #cv.generic_visit(tree)

def getToken(code):
    tree = ast.parse(code)
    array = sorted({node.id for node in ast.walk(tree) if isinstance(node, ast.Name)})
    result = []
    for i in array:
        result += camelSplit(i)
    return result

def camelSplit(word):
    result = []
    temp = word[0]
    for i in word[1:]:
        if (i.isupper()):
            result.append(temp.lower())
            temp = i
        else:
            temp += i
    result.append(temp.lower())
    return result




code = "def add(arg1, arg2):\n\tprint(arg1)\n\treturn arg1+arg2\nadd(1,2)\n"
code2 = "class SomeClass:\n\tdef printFirst():\n\t\tprint(\"x\")\n\tdef printSecond():\n\t\tself.printFirst()\nsomeInstance=SomeClass()\nsomeInstance.printSecond()\n"
#print(getMethodName(code))
#print(getToken(code))
#print(getAPISequence(code))
#printAST(code2)
print(getAPISequence(code2))
print(getMethodName(code2))
print(getToken(code2))