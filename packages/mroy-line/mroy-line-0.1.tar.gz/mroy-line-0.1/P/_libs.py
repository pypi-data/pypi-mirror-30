import sys,os

import pickle as pickle2
import dill as pickle

from contextlib import contextmanager

import termcolor

ROOT = "/tmp/psession"

if not os.path.exists(ROOT):
    os.mkdir(ROOT)

@contextmanager
def stdout(f):
    try:
        tmp = sys.stdout
        sys.stdout = f
        yield
    except Exception as e:
        raise e
    finally:
        sys.stdout = tmp


class _attrs:
    pass

class _functions:
    pass

class Sess:

    def __init__(self, token):
        self.token = token
        self.tmp_file = os.path.join(ROOT,token)
        self._attres = dict()
        self._inputs = []
        sys.path.insert(0, "")
        if not os.path.exists(self.tmp_file) or not os.path.exists(self.tmp_file+ ".pyd"):
            self.save()
        self.load()
        # self._functions = _functions()

    def clear(self):
        self._attres = dict()
        self._inputs = []
        self.save()

    def save(self):
        # with open(self.tmp_file+"f", "wb") as fp:
            # pickle.dump(self._functions,fp)

        with open(self.tmp_file, "wb") as fp:
            pickle.dump(self._attres,fp)
        
        with open(self.tmp_file + ".pyd" , "wb") as fp:
            pickle.dump(self._inputs, fp)

    def load(self):
        if not os.path.exists(self.tmp_file):
            termcolor.cprint("no such file", "red")
            return 

        # with open(self.tmp_file + "f", "rb") as fp:
        #     self._functions = pickle.load(fp)
        try:
            with open(self.tmp_file, "rb") as fp:
                self._attres = pickle.load(fp)
        except Exception:
            with open(self.tmp_file, "rb") as fp:
                self._attres = pickle2.load(fp)
        try:
            with open(self.tmp_file + '.pyd', "rb") as fp:
                self._inputs = pickle.load(fp)
        except Exception:
            with open(self.tmp_file + '.pyd', "rb") as fp:
                self._inputs = pickle2.load(fp)

    def search(self,w):
        if hasattr(self._attres, w):
            return "self.sess._attres." + w
        return w
    
    def add_attr(self, w, v):
        self._attres[w] = v

    def add_input(self, i):
        self._inputs.append(i)

    def __getitem__(self, i):
        if isinstance(i, int):
            return self._inputs[i]
        elif isinstance(i, str):
            return self._attres[i]

    def __setitem__(self,  name, value):
        self._attres[name] = value


    # def add_attr(self,w, v):
    #     if not "self.sess._attres." in w:
    #         setattr(self._attres, w.strip(), v)
    #     else:
    #         w = w.replace("self.sess._attres.", "")
            
    #         setattr(self._attres, w.strip(), v)
            
    def print_in(self, inline):
        s = termcolor.colored("[%d]" % len(self._inputs), 'green')  + ": " + termcolor.colored(inline, "yellow")
        print(s)

    def print_out(self, out):
        s = termcolor.colored("=>", 'red') + str(out)
        print(s)

