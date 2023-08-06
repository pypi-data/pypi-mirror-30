
import logging
import json

from populater				import Populater

log					= logging.getLogger('Restruct')
# log.setLevel(logging.DEBUG)


class Collection( object ):

    def __init__(self, data):
        self.data			= data

    def format(self, struct):
        return Restruct(self.data, struct)


class Frame( object ):

    def __init__(self, data, parent=None, index=None):
        self.parent			= parent
        self.index			= index
        self.data			= data

    def source(self, key=None):
        if self.parent is None:
            return None
        else:
            return self.parent.data if key is None else self.parent.data[key]

    def keys(self):
        return list(self.data.keys())

    def values(self):
        return list(self.data.values())

    def child(self, k):
        keys				= self.data.keys() if type(self.data) is dict else range(0,len(self.data))
        if k not in keys:
            return None
        return Frame(self.data[k], self, k)

    def children(self):
        return list(map(lambda k: self.child(k), self.keys()))

    def root(self):
        frame				= self
        while frame.parent:
            frame			= frame.parent
        return frame


class Restructure( object ):

    def __init__(self, data, struct):
        root				= Frame(data)
        self.result			= {}
        
        self.extend( root, struct, self.result )

    def data(self):
        return self.result

    def extend(self, frame, struct, result):
        if frame is None:
            raise Exception("Frame cannot be none")
        
        data				= frame.data
        log.debug("Extending Data[{}] with struct {}".format(frame.index, struct))

        if type(data) is list:
            log.debug("Data is a list, sending to extend_list()")
            return self.extend_list(frame, struct, result)

        fill				= Populater(data, frame)
        keys				= list(range(0,len(struct))) if type(struct) is list else struct.keys()

        log.debug("Found {} keys for struct {}".format(len(keys), keys))
        for key in keys:
            # log.debug("Building result {}".format(json.dumps(result, indent=4)))
            v				= struct[key]
            
            if key == Restruct.flattenTrigger:
                result[key]		= v
                continue

            spot			= result
            k				= fill(key) if type(key) is str else key

            if k is None:
                continue
            elif type(k) is list:
                for i,tk in enumerate(k):
                    if result.get(tk) == None:
                        result[tk]	= {}
                    result		= result[tk]

                k			= k[i]
                Restruct.lastDynamicKey	= k

            # data[Restruct.keyKey]	= Restruct.lastDynamicKey

            if result.get(k) is None:
                if v is True:
                    result[k]		= data[k]
                elif type(v) is str:
                    result[k]		= fill(v)
                elif type(k) is list:
                    first		= v[0]
                    if type(first) is str:
                        result[k]	= fill(first)
                    elif type(first) in (list, dict):
                        result[k]	= [ self.extend(frame, first, {}) ]
                    else:
                        result[k]	= [ first ]
                elif v is False:
                    del result[k]
                else:
                    result[k]		= self.extend(frame, v, {})
            else:
                log.debug("Data for key {} already exists".format(k))
                if type(v) is list:
                    value		= v[0]
                    if type(value) is str:
                        value		= fill(v[0])
                    elif type(value) in (list, dict):
                        value		= self.extend(frame, value, {})
                    result[k].append(value)
                elif type(v) in (list, dict):
                    log.debug("Move scope to sub level {}".format(k))
                    self.extend(frame, v, result[k])

        # NOTE: not sure if this applies in python.  Need to find another method to determine if
        # something was meant to be removed
        # 
        # if result.get(k) is None:
        #     del result[k]
        if type(struct) is list:
            return list( map(lambda k: result[k], result.keys()) )
        else:
            return result

    def extend_list(self, frame, struct, result):
        rows				= frame.data

        if len(rows) == 0:
            pass
        else:
            for i,row in enumerate(rows):
                # row[Restruct.indexKey]	= int(i)
                # row[Restruct.parentKey]	= rows
                child			= frame.child(i)
                if child is None:
                    raise Exception("Invalid index '{}'.  Data: {}".format(i, frame.data))
                self.extend(child, struct, result)
        return result
                

    
def Structure(struct):
    def wrap(data):
        return Restruct(data, struct)
    return wrap

def flatten(result, flattened=None):
    if type(result) is dict:
        flag				= result.get( Restruct.flattenTrigger )
        keys				= result.keys()
    else:
        flag				= None
        keys				= list(range(0,len(result)))
        
    log.debug("Checked for flatten flag in keys {}".format(keys))
        
    if flag is not None:
        del result[ Restruct.flattenTrigger ]

    if flattened is None:
        flattened			= []

    flattened.append( id(result) )
    for k in keys:
        child				= result[k]
        if type(child) in (list, dict) and id(child) not in flattened:
            result[k]			= flatten(result[k], flattened)

    if flag is True:
        keys				= list(result.keys())
        keys.sort()
        result				= list(map(lambda i: result[i], keys))

    return result
    
    
def Restruct( data, struct ):
    if not type(struct) in (list, dict):
        raise Exception("Bad Structure: structure is not a dict: type {}".format(type(struct)))

    struct				= json.loads(json.dumps(struct))
    restructured			= Restructure(data, struct).data()
    flattened				= flatten(restructured)

    return flattened

def method(name=None, fn=None, err=None):
    if fn is None:
        def wrap(f):
            Populater.method(f.__name__, f, err)
            return f
        return wrap
    Populater.method(name, fn, err)

Restruct.flattenTrigger			= "__array"
Restruct.rescopeTrigger			= "__rescope"
Restruct.keyKey				= "$key"
Restruct.indexKey			= "$index"
Restruct.parentKey			= "$parent"
Restruct.lastDynamicKey			= None
Restruct.structure			= Structure
Restruct.collection			= Collection
Restruct.populater			= Populater
Restruct.method				= method
