import os
import sys
from Products.Five import zcml

_PATH_REGISTRY = {}

def setup_pythonpath(basedir):
    """Add all directories inside the basedir to the system PYTHONPATH.
    """
    
    valid = [d for d in os.listdir(basedir) if not d.startswith('.') and \
               os.path.isdir(os.path.join(basedir, d))]

    global _PATH_REGISTRY
    items = _PATH_REGISTRY.get(basedir, [])
    _PATH_REGISTRY[basedir] = items
    for entry in valid:
        full = os.path.join(basedir, entry)
        if full not in sys.path and full not in items:
            sys.path.append(full)
            items.append(full)
            
            last = ''
            for x in entry.split('.'):
                v = last
                if v:
                    v += '.'
                v += x
                
                # if the module has already been loaded and is being
                # pulled from somewhere else, we need to add it here
                if sys.modules.has_key(v):
                    f = os.path.join(full, '/'.join(v.split('.')))
                    m = sys.modules[v]
                    if f not in m.__path__:
                        m.__path__.append(f)
                last = v

    return items

def load_extrazcml(items):
    """Load all of the configure.zcml's for the given packages.
    """

    for entry in items:
        m = __import__(entry, {}, {}, entry)
        
        try:
            zcml.load_config('configure.zcml', m)
        except IOError: # No file
            pass
