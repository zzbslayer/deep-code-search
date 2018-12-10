from parsePython import *
from code2vec import *
from UseData import *
import json
import numpy as np
from TCA import TCA
from flask import Flask
from flask_cors import *
app = Flask(__name__)
CORS(app, supports_credentials=True)

java_data = {17:"public static String getNextTag ( String xmlData , int position ) { String nextTag = null ; if ( xmlData != null && ! xmlData . isEmpty ( ) && position < xmlData . length ( ) && xmlData . substring ( position ) . contains ( "<" ) ) { while ( xmlData . charAt ( position ) != '<' ) { position ++ ; } int startIndex = position ; if ( xmlData . substring ( position ) . contains ( ">" ) ) { while ( xmlData . charAt ( position ) != '>' ) { position ++ ; } nextTag = xmlData . substring ( startIndex , position + 1 ) ; } } return nextTag ; } ",
7:"public float bottom ( float margin ) { return pageSize . bottom ( marginBottom + margin ) ; } ",
12:"public RGBColor toGreyScale ( ) { return new RGBColor ( 0.30 * getRed ( ) + 0.59 * getGreen ( ) + 0.11 * getBlue ( ) ) ; } ",
21:"public void addClientSocketListener ( ClientSocketListener listener ) { if ( listener == null ) throw new NullPointerException ( ) ; listeners . add ( listener ) ; }",
23:"final void addProcessToGcListLocked ( ProcessRecord proc ) { boolean added = false ; for ( int i = mProcessesToGc . size ( ) - 1 ; i >= 0 ; i -- ) { if ( mProcessesToGc . get ( i ) . lastRequestedGc < proc . lastRequestedGc ) { added = true ; mProcessesToGc . add ( i + 1 , proc ) ; break ; } } if ( ! added ) { mProcessesToGc . add ( 0 , proc ) ; } } ",
34:"public boolean isFocused ( ) { if ( m_Control == null ) return false ; return m_Control . isFocusControl ( ) ; } ",
36:"public static long getFreeDiskSpace ( boolean checkInternal ) { String status = Environment . getExternalStorageState ( ) ; long freeSpace = 0 ; if ( status . equals ( Environment . MEDIA_MOUNTED ) ) { freeSpace = freeSpaceCalculation ( Environment . getExternalStorageDirectory ( ) . getPath ( ) ) ; } else if ( checkInternal ) { freeSpace = freeSpaceCalculation ( \"/\" ) ; } else { return - 1 ; } return freeSpace ; }",
38:"public void removePropertyChangeListener ( String name , PropertyChangeListener pcl ) { m_bcSupport . removePropertyChangeListener ( name , pcl ) ; } ",
40:"public void incDfsUsed ( long value ) { used . addAndGet ( value ) ; } ",
49:"public void removeElements ( List elements ) { if ( elements . size ( ) > 0 ) { fElements . removeAll ( elements ) ; if ( fTable != null ) { fTable . remove ( elements . toArray ( ) ) ; } dialogFieldChanged ( ) ; } } "
            }

py_data = {17:"def getNextTag(xmlData, position):\n\tnextTag = None\n\tif xmlData!=None and xmlData!='' and position < len(xmlData) and '<' in xmlData[position:]:\n\t\twhile xmlData[position]!='<':\n\t\t\tposition+=1\n\t\tstartIndex = position\n\t\tif '>' in xmlData[position:]:\n\t\t\twhile xmlData[position] !='>':\n\t\t\t\tposition+=1\n\t\t\tnextTag = xmlData[startIndex:position+1]\n\treturn nextTag",
7:"def bottom(margin):\n\treturn pageSize.bottom(marginBottom+margin)",
12:"def toGreyScale():\n\treturn RGBColor(0.30*getRed() + 0.59*getGreen() + 0.11*getBlue())",
21:"def addClientSocketListenser(listener):\n\tif listener == None:\n\t\traise NullPointerException()\n\tlisteners.add(listener)",
23:"def addProcessToGcListLocked(proc):\n\tadded = False\n\tfor i in range(mProcessesToGc.size()-1, 0, -1):\n\t\tif mProcessesToGc.get(i).lastRequestedGc < proc.lastRequestedGc:\n\t\t\tadded = True\n\t\t\tmProcessesToGc.add(i+1, proc)\n\t\t\tbreak\n\tif not added:\n\t\tmProcessesToGc.add(0, proc)",
34:"def isFocused():\n\tif m_Control==None:\n\t\treturn False\n\treturn m_Control.isFocusControl()",
36:"def getFreeDiskSpace(checkInternal):\n\tstatus=Environment.getExternalStorageState()\n\tfreeSpace = 0\n\tif status.equals(Environment.MEDIA_MOUNTED):\n\t\tfreeSpace = freeSpaceCalculation(Environment.getExternalStorageDirectory().getPath())\n\telif checkInternal:\n\t\tfreeSpace = freeSpaceCalculation(\"/\")\n\telse:\n\t\treturn -1\n\treturn freeSpace",
38:"def removePropertyChangeListener(name, pcl):\n\tm_bcSupport.removePropertyChangeListener(name, pcl)",
40:"def incDfsUsed(value):\n\tused.addAndGet(value)",
49:"def removeElements(elements):\n\tif len(elements)>0:\n\t\tfElements.removeAll(elements)\n\t\tif fTable!=None:\n\t\t\tfTable.remove(elements.toArray())\n\t\tdialogFieldChange()"
         }

def move(l1, l2):
    result = []
    flag = False
    for i in l2:
        for j in l1:
            if i==j:
                result.append(j)
                flag = True
                break
        if (flag == False):
            result.append(0)
        else:
            flag = False
    for k in l1:
        if k not in result:
            result.append(k)
    return result

def pad(x, size):
    if size <= len(x):
        return x[:size]
    out = [0]*size
    out[:len(x)] = x
    return out
    
def get_vec(java_data, py_data):
    _cv = CodeVisitor()
    _c2v = Code2Vec()
    _ud = UseData()
    _m, _a, _t = _ud.load_use_data()
    Xs = []
    Xt = []
    for i in java_data:
        py_token = _cv.getToken(py_data[i])
        py_api = _cv.getAPISequence(py_data[i])
        py_meth = _cv.getMethodName(py_data[i])
        py_token_vec = _c2v.convert_tokens(py_token)
        py_apiseq_vec = _c2v.convert_apiseq(py_api)
        py_meth_vec= _c2v.convert_methname(py_meth)
        
        java_token_vec = _t[i-1]
        java_apiseq_vec = _a[i-1]
        java_meth_vec = _m[i-1]
        
        py_token_vec = move(py_token_vec, java_token_vec)
        py_apiseq_vec = move(py_apiseq_vec, java_apiseq_vec)
        py_meth_vec = move(py_meth_vec, java_meth_vec)
        
        padded_java_token_vec = pad(java_token_vec, 50)
        padded_java_apiseq_vec = pad(java_apiseq_vec, 30)
        padded_java_meth_vec = pad(java_meth_vec, 6)
        
        padded_py_token_vec = pad(py_token_vec, 50)
        padded_py_apiseq_vec = pad(py_apiseq_vec, 30)
        padded_py_meth_vec = pad(py_meth_vec, 6)
        
        temp1 = np.concatenate((padded_java_meth_vec, padded_java_apiseq_vec, padded_java_token_vec), axis=0)
        Xs.append(temp1)
        temp2 = np.concatenate((padded_py_meth_vec, padded_py_apiseq_vec, padded_py_token_vec), axis=0)
        Xt.append(temp2)
    return Xs, Xt

def Euclidean(v1, v2):
    return np.linalg.norm(v1-v2)

def Manhattan(v1, v2):
    return np.linalg.norm(v1-v2,ord=1)

def Cosine(v1, v2):
    return np.dot(v1,v2)/(np.linalg.norm(v1)*(np.linalg.norm(v2)))

def get_transferred_vec(jdata, pdata):
    Xs, Xt = get_vec(jdata, pdata)
    tca = TCA(np.array(Xs), np.array(Xt), dim=6 + 30 +  50)
    return tca.fit()

def euclidean_list(Xs, Xt):
    result = []
    for i in Xs:
        temp = []
        for j in Xt:
            temp.append(Euclidean(i, j))
        result.append(temp)
    return result

def manhattan_list(Xs, Xt):
    result = []
    for i in Xs:
        temp = []
        for j in Xt:
            temp.append(Manhattan(i, j))
        result.append(temp)
    return result

def cosine_list(Xs, Xt):
    result = []
    for i in Xs:
        temp = []
        for j in Xt:
            temp.append(Manhattan(i, j))
        result.append(temp)
    return result

@app.route("/data")
def data():
    Xs, Xt = get_vec(java_data, py_data)
    labels = []
    for i in range(len(Xs)):
        labels.append(i)
    for i in range(len(Xs)):
        labels.append(i)
    return json.dumps({'pyData':np.array(Xt).tolist(), 'javaData':np.array(Xs).tolist()})

@app.route("/transferred-data")
def transferred_data():
    Xs_new, Xt_new = get_transferred_vec(java_data, py_data)
    return json.dumps({'pyData':Xt_new.tolist(), 'javaData':Xs_new.tolist()})

@app.route("/distance/euclidean/transferred")
def transferred_euclidean():
    Xs_new, Xt_new = get_transferred_vec(java_data, py_data)
    result = euclidean_list(Xs_new, Xt_new)
    return json.dumps(result)

@app.route("/distance/manhattan/transferred")
def transferred_manhattan():
    Xs_new, Xt_new = get_transferred_vec(java_data, py_data)
    result = manhattan_list(Xs_new, Xt_new)
    return json.dumps(result)

@app.route("/distance/cosine/transferred")
def transferred_cosine():
    Xs_new, Xt_new = get_transferred_vec(java_data, py_data)
    result = cosine_list(Xs_new, Xt_new)
    return json.dumps(result)


@app.route("/distance/euclidean")
def euclidean():
    Xs, Xt = get_vec(java_data, py_data)
    result = euclidean_list(Xs, Xt)
    return json.dumps(result)

@app.route("/distance/manhattan")
def manhattan():
    Xs, Xt = get_vec(java_data, py_data)
    result = []
    for i in Xs:
        temp = []
        for j in Xt:
            temp.append(Manhattan(i, j))
        result.append(temp)
    return json.dumps(result)

@app.route("/distance/cosine")
def cosine():
    Xs, Xt = get_vec(java_data, py_data)
    result = []
    for i in Xs:
        temp = []
        for j in Xt:
            temp.append(Cosine(i, j))
        result.append(temp)
    return json.dumps(result)

if __name__ == "__main__":
    #print(JSONdata())
    app.run()
