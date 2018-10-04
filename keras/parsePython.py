import ast

class CodeVisitor(ast.NodeVisitor): 

    def __init__(self):
        self.methodName = []
        self.nodeType = ""
        self.apiSequence = []

        self.classInstance = {}

        self.classLevel = -1

        # e.g. temp = A()
        #
        # self.tempClass = A
        # 
        # it will be append to the dictionary self.classInstance
        self.tempClass = "" 

        # e.g. class A:
        #          def a:
        #              ...
        #
        # self.generalClass = A
        self.generalClass = ""

    def clear(self):
        self.methodName = []
        self.nodeType = ""
        self.apiSequence = []
        self.classInstance = {}
        self.classLevel = -1
        self.tempClass = ""
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
                    """
                    Expression - 
                    """
                    if (char == 'N'):
                        message = message[19:]
                        api = ""
                        for i in message:
                            if (i == "'"):
                                break
                            api += i
                        self.apiSequence.append(api)
                        #print(api)
                    elif (char == 'A'):  #Attribute
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
                            className = self.classInstance.get(instanceName, "")

                        methodName = ""
                        for i in message:
                            if (i =="'"):
                                break
                            methodName += i
                        if (className == ""):
                            self.apiSequence.append(methodName)
                        else:
                            self.apiSequence.append(className + "." + methodName)
                        
                    #print(message[10:])
                    #self.apiSequence.append(api)

                elif (className == "Assign"):
                    #print("Assign:")
                    assignInfo = fields[1][1]
                    #print(fields)
                    #print(fields[1][1])
                    className = ""
                    if (assignInfo[0] == 'D'):
                        className = "Dict"
                    elif (assignInfo[0] == 'L'):
                        className = "List"
                    elif (assignInfo[0] == 'C' or assignInfo[0] == 'S'):
                        assignInfo = assignInfo[assignInfo.find("id"):]
                        for char in assignInfo[4:]:
                            if (char !="'"):
                                className += char
                            else:
                                break
                    self.apiSequence.append(className + ".new")
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
        self.clear()
        self.nodeType = "print"
        self.ast_visit(node)

    def visit_MethodName(self, node):
        self.clear()
        self.nodeType = "FunctionDef"
        self.ast_visit(node) 
        return self.methodName

    def visit_Statement(self, node): 
        self.clear()
        self.nodeType = "Statement"
        self.ast_visit(node) 
        return self.apiSequence

    def printAST(self, code):
        tree = ast.parse(code)
        self.visit_print(tree)

    def getAPISequence(self, code):
        tree = ast.parse(code)
        return self.visit_Statement(tree)

    def getMethodName(self, code):
        tree = ast.parse(code)
        return self.visit_MethodName(tree)
        #cv.generic_visit(tree)

    def getToken(self, code):
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

if __name__ == '__main__':
    #code = "def add(arg1, arg2):\n\tprint(arg1)\n\treturn arg1+arg2\nadd(1,2)\n"
    cv = CodeVisitor()
    #code2 = "class SomeClass:\n\tdef printFirst():\n\t\tprint(\"x\")\n\tdef printSecond():\n\t\tself.printFirst()\nsomeInstance=SomeClass()\nsomeInstance.printSecond()\n"
    code2 = "def encode(key, string):\n\ttest={}\n\tencoded_chars = []\n\tfor i in xrange(string):\n\t\tkey_c = key[i % len(key)]\n\t\tencoded_c = chr(ord(string[i]) + ord(key_c) % 256)\n\t\tencoded_chars.append(encoded_c)\n\tencoded_string = \"\".join(encoded_chars)\n\treturn base64.urlsafe_b64encode(encoded_string)"
    cv.printAST(code2)
    #token = cv.getToken(code2)
    #methodname = cv.getMethodName(code2)
    APISequence = cv.getAPISequence(code2)
    
    #print(token)
    #print(methodname)
    print(APISequence)
    #code3="import posixpath\nimport os.path\n\n_os_alt_seps = list(sep for sep in [os.path.sep, os.path.altsep]\n                    if sep not in (None, '/'))\n\ndef safe_join(directory, filename):\n    # docstring omitted for brevity\n    filename = posixpath.normpath(filename)\n    for sep in _os_alt_seps:\n        if sep in filename:\n            raise NotFound()\n    if os.path.isabs(filename) or \\\n       filename == '..' or \\\n       filename.startswith('../'):\n        raise NotFound()\n    return os.path.join(directory, filename)\n"