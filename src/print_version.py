
import sys
import hashlib

from IPython.core.magic import magics_class, Magics, line_magic, line_cell_magic

@magics_class
class VersionPrinter(Magics):
    def __init__(self, *a, **kw):
        super(VersionPrinter, self).__init__(*a, **kw)
        self.loaded_modules = set()
        self.print = None
        self.cell = None

    def compute_hash(self, path):
        with open(path, 'rb') as f:
            binary = f.read()
        md5hash = hashlib.md5(binary)
        return md5hash.hexdigest()

    @line_magic
    def print_version(self, line):
        self.print = False if self.print is None else None
        #self.print = not self.print
        if self.print is not None:
            print("turn on version printer on modules")
       
    @line_cell_magic
    def check_version(self, line='', cell=None):
        if cell is None:
            self.toggle_check_version(line)
        else:
            self.cell = cell
            for line in cell.split('\n'):
                results = re.search("^import ([a-zA-Z\.\_]+)", line)
                if results is not None:
                    print(results.group[0])
    
    def pre_run_cell(self):
        if self.print:
            self.loaded_modules = set(sys.modules)

    def post_run_cell(self):
        if self.print is False:
            self.print = True
        elif self.print:
            newly_loaded_modules = set(sys.modules) - self.loaded_modules
            newly_loaded_modules = set([module_name.split('.')[0] for module_name in newly_loaded_modules])
            #print(newly_loaded_modules)
            for module_name in newly_loaded_modules:
                module = sys.modules[module_name]
                if hasattr(module, '__version__'):
                    version = module.__version__
                    print(f"{module_name} : version = {version}")
                elif hasattr(module, '__file__'):
                    path = module.__file__
                    hash_val = self.compute_hash(path)
                    print(f"{module_name} : hash value = {hash_val}")
        self.cell = None


ip = get_ipython()

version_printer = VersionPrinter(ip)
ip.register_magics(version_printer)
ip.events.register('pre_run_cell', version_printer.pre_run_cell)
ip.events.register('post_run_cell', version_printer.post_run_cell)
