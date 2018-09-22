import ast

class CodeVisitor(ast.NodeVisitor): 
    methodName = []
    nodeType = ''
    apiSequence = []
    def __init__(self):
        self.methodName = []
        self.nodeType = ''
        self.apiSequence = []

    def str_node(self, node):
        if isinstance(node, ast.AST):
            className = node.__class__.__name__

            fields = [(name, self.str_node(val)) for name, val in ast.iter_fields(node) if name not in ('left', 'right')]
            rv = '%s(%s' % (className, ', '.join('%s=%s' % field for field in fields))

            if (self.nodeType == "FunctionDef"):
                if ( className == self.nodeType):
                    fname = fields[0][1]
                    fname = fname[1:-1] # convert "'function'" to "function"
                    self.methodName.append(fname)
            elif (self.nodeType == "Statement"):
                if (className == "Expr"):
                    print("Expr:")
                    message = fields[0][1]
                    print(fields)
                    #print(message[10:])

                elif (className == "Assign"):
                    #print("Assign:")
                    callInfo = fields[1][1]
                    #print(fields[1])
                    callInfo = callInfo[callInfo.find("id"):]
                    api = ""
                    for char in callInfo[4:]:
                        if (char !="'"):
                            api += char
                        else:
                            break
                    self.apiSequence.append(api)
            return rv + ')'
        else:
            return repr(node)

    def ast_visit(self, node, level=0):
        message = self.str_node(node)
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

    def visit_FunctionDef(self, node):
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
    return cv.visit_FunctionDef(tree)
    #cv.generic_visit(tree)

def getToken(code):
    tree = ast.parse(code)
    return sorted({node.id for node in ast.walk(tree) if isinstance(node, ast.Name)})


code = "def add(arg1, arg2):\n\tprint(arg1)\n\treturn arg1+arg2\nadd(1,2)\n"
code2 = "class A:\n\tdef a():\n\t\tprint(\"x\")\n\tdef b():\n\t\tself.a()\ntest=A()\ntest.b()\n"
#print(getMethodName(code))
#print(getToken(code))
#print(getAPISequence(code))
printAST(code2)
print(getAPISequence(code2))