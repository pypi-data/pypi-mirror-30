import sys,os
import pickle as pickle2
import dill as pickle
import termcolor
from shutil import copyfile
from curses import setupterm
from curses import tparm
from curses import tigetstr
from contextlib import contextmanager
from io import BufferedIOBase
from types import FunctionType
from types import GeneratorType, BuiltinFunctionType, BuiltinMethodType
from collections import  Iterable


setupterm()

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
        self._pre_config = set()
        self.history = []
        sys.path.insert(0, "")
        if not os.path.exists(self.tmp_file) or not os.path.exists(self.tmp_file+ ".pyd"):
            self.save()
        self.load()
        # self._functions = _functions()

    def clear(self):
        self._attres = dict()
        self._inputs = []
        self._pre_config = set()
        self.save()

    def get_hist(self):
        return '\n'.join(self.history)

    def _interact(self, pre='>', default='y'):
        v = input(pre)
        if not v:
            return default
        return v

    def save_io(self, name, attr):
        _dirs = [i for i in attr.__dir__() if not i.startswith("_")]
        for i in _dirs:
            termcolor.cprint(str(i),'blue',end=" ")
        print("")
        while 1:
            handle = self._interact("{}={}.".format(name, name), default="read()")
            handle = "{}={}.".format(name, name) + handle
            try:
                exec(handle, self._attres, self._attres)
                self._inputs.append(handle)
                self.history.append(handle+"\n")
            except Exception as e:
                termcolor.cprint("[" + handle + "]", 'red', end="|")
                termcolor.cprint(e, 'red')
                continue
            break

    def save(self):
        # with open(self.tmp_file+"f", "wb") as fp:
            # pickle.dump(self._functions,fp)
        for attr_name in self._attres:
            if isinstance(self._attres[attr_name], BufferedIOBase):
                termcolor.cprint("Io can not be serilailze Handle it (read,write):", 'red')
                self.save_io(attr_name, self._attres[attr_name])
        if os.path.exists(self.tmp_file):
            bak_file = copyfile(self.tmp_file, self.tmp_file + ".bak")
            bak_d_file = copyfile(self.tmp_file, self.tmp_file + ".pyd" + ".bak")
            bak_pyc_file = copyfile(self.tmp_file, self.tmp_file + ".pyccc" + ".bak")
            bak_hist_file = copyfile(self.tmp_file, self.tmp_file + ".hist" + ".bak")

        with open(self.tmp_file + ".pyd" , "wb") as fp:
            pickle2.dump(self._inputs, fp)

        with open(self.tmp_file + ".pyccc" , "wb") as fp:
            pickle2.dump(self._pre_config, fp)

        with open(self.tmp_file + ".hist" , "w") as fp:
            fp.write('\n'.join(self.history))

        try:
            with open(self.tmp_file, "wb") as fp:
                pickle.dump(self._attres,fp)
        except Exception as e:
            os.rename(bak_file, self.tmp_file)
            os.rename(bak_d_file, self.tmp_file + ".pyd")
            os.rename(bak_pyc_file, self.tmp_file + ".pyccc" )
            os.rename(bak_hist_file, self.tmp_file + ".hist")

    def load(self):
        if not os.path.exists(self.tmp_file):
            termcolor.cprint("no such file", "red")
            return

        if not os.path.exists(self.tmp_file + ".hist"):
            termcolor.cprint("no such hist file " , "red")
            return

        with open(self.tmp_file + ".hist") as fp:
            self.history = fp.readlines()

        # with open(self.tmp_file + "f", "rb") as fp:
        #     self._functions = pickle.load(fp)
        try:
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

            if os.path.exists(self.tmp_file + '.pyccc'):
                with open(self.tmp_file + '.pyccc', "rb") as fp:
                    self._pre_config = pickle2.load(fp)


        except ModuleNotFoundError:
            print("Path uncorrect")
            sys.exit(1)

    def search(self,w):
        if hasattr(self._attres, w):
            return "self.sess._attres." + w
        return w

    def add_preconfig(self, f):
        if f in self._pre_config:
            return False

        self._pre_config.add(f)
        return True

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

    # def print_out(self, out):

    #     s = termcolor.colored("=> ", 'red') + str(out)
    #     print(s)
    #     if isinstance(out, (FunctionType,  BuiltinFunctionType, BuiltinMethodType,)):
    #         self.print_out(out())
    #     elif isinstance(out, (GeneratorType,Iterable)):
    #         for i in out:
    #             s = termcolor.colored("    ->", 'red')
    #             print(s,i)
    #             r = input("[AnyPress /Enter Next]")
    #             if r.strip():
    #                 break
    def print_out(self, out):
        s = termcolor.colored("=> ", 'red') + str(out)
        print(s)


    def eprint_out(self, out):
        with Display.jump(20, 2):
            with Display.reverse():
                with Display.bold():
                    print("          ")
                    print("  OUTPUT  ")
                    print("          ")
            s = termcolor.colored("=> ", 'red') + str(out)
            print(s)
            # if isinstance(out, (FunctionType,  BuiltinFunctionType, BuiltinMethodType,)):
                # res = out()
                # print("-------------- FunctionType --------")
                # print(termcolor.colored("=> ", 'red'), res)
            # elif isinstance(out, (GeneratorType,Iterable)):
                # for i in out:
                    # s = termcolor.colored("    ->", 'red')
                    # print(s,i)
                    # r = input("[AnyPres /En Next]")
                    # if r.strip():
                        # break



class Display:

    @staticmethod
    @contextmanager
    def jump(row, col=0):
        try:
            tparm(tigetstr("sc"))
            os.system("tput sc && tput civis && tput clear && tput cup %d,%d  " % (row, col))
            os.system("tput cnorm")
            yield
        finally:
            input("End")
            os.system("tput clear && tput sgr0  && tput rc")

    @contextmanager
    def uline():
        try:
            os.system("tput smul")
            yield
        finally:
            os.system("tput rmul")

    @contextmanager
    def reverse():
        try:
            os.system("tput rev")
            yield
        finally:
            os.system("tput sgr0")


    @contextmanager
    def bold():
        try:
            os.system("tput bold")
            yield
        finally:
            os.system("tput sgr0")
