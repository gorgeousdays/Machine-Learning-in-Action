import io, os,sys,types
from IPython import get_ipython
from nbformat import read
from IPython.core.interactiveshell import InteractiveShell
 
class NotebookFinder(object):
    def __init__(self):
        self.loaders = {}
 
    def find_module(self, fullname, path=None):
        nb_path = find_notebook(fullname, path)
        if not nb_path:
            return
 
        key = path
        if path:
            # lists aren't hashable
            key = os.path.sep.join(path)
 
        if key not in self.loaders:
            self.loaders[key] = NotebookLoader(path)
        return self.loaders[key]
 
def find_notebook(fullname, path=None):
    name = fullname.rsplit('.', 1)[-1]
    if not path:
        path = ['']
    for d in path:
        nb_path = os.path.join(d, name + ".ipynb")
        if os.path.isfile(nb_path):
            return nb_path
        # let import Notebook_Name find "Notebook Name.ipynb"
        nb_path = nb_path.replace("_", " ")
        if os.path.isfile(nb_path):
            return nb_path
 
class NotebookLoader(object):
    def __init__(self, path=None):
        self.shell = InteractiveShell.instance()
        self.path = path
 
    def load_module(self, fullname):
        path = find_notebook(fullname, self.path)
 
        print ("importing Jupyter notebook from %s" % path)
 
 
        # load the notebook object
        with io.open(path, 'r', encoding='utf-8') as f:
            nb = read(f, 4)
 
 
        # create the module and add it to sys.modules
        # if name in sys.modules:
        #    return sys.modules[name]
        mod = types.ModuleType(fullname)
        mod.__file__ = path
        mod.__loader__ = self
        mod.__dict__['get_ipython'] = get_ipython
        sys.modules[fullname] = mod
 
        # extra work to ensure that magics that would affect the user_ns
        # actually affect the notebook module's ns
        save_user_ns = self.shell.user_ns
        self.shell.user_ns = mod.__dict__
 
        try:
            for cell in nb.cells:
                if cell.cell_type == 'code':
                # transform the input to executable Python
                    code = self.shell.input_transformer_manager.transform_cell(cell.source)
                    exec(code, mod.__dict__)  #注意此处的缩进
        finally:
            self.shell.user_ns = save_user_ns
        return mod
sys.meta_path.append(NotebookFinder())