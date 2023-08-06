import pkgutil
import sys
import os
import importlib
import importlib.util
        
def dynsceneloader(scenename):
    path = os.path.join(os.getcwd(), "scenes")
    modules = pkgutil.iter_modules(path=[path])
    
    for loader, mod_name, ispkg in modules:
        if mod_name not in sys.modules:
            spec = importlib.util.spec_from_file_location("module.name", path+"/"+mod_name+".py")
            loaded_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(loaded_mod)
            loaded_class = getattr(loaded_mod, mod_name)
            return loaded_class    
    
    
    