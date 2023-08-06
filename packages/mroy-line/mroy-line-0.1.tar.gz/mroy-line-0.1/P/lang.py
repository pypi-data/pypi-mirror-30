import re,sys, os
import importlib
from termcolor import colored, cprint
from P._libs import Sess
from types import  FunctionType

class PyError(Exception):
    pass


class LangTree:
    def __init__(self, sess):
        self.sess = sess
        self.module("import sys, os")
        sys.path.insert(0, "")
        # self.sess._attres = globals()

    def module(self, string):
        group = re.match(r'^(?P<l>import|from)\s+(?P<lc>(?:\w+\.?)+)\s*(?P<r>import)?\s*(?P<rc>(?:\w+\.?)*)\s*(as)?\s*(?P<n>\w+)?', string)
        if not group:
            return
        if not group.group("l"):
            return

        import_str = group.group("lc")
        attrs = None

        if group.group("l") == 'from':
            if group.group("r") != 'import' or not group.group("rc"):
                return
            attrs = group.group("rc")
        
        
        name = group.group("n")
        lib = importlib.import_module(import_str)

        if attrs:
            lib = getattr(lib, attrs)

        if not name:
            if hasattr(lib, '__name__'):
                name = lib.__name__
            else:
                name = attrs
        
        self.sess.add_attr(name, lib)
        return True

    def cmd(self, string):
        if string[1:] == "list":
            for i in self.sess._attres.__dict__:
                cprint(i + " =>" + str(self.sess._attres.__dict__[i]), 'green')

    
    def eval(self, string):
        try:
            res = eval(string)
            return res
        except Exception as e:
            cprint(e + string, "red")
            raise PyError(string)



    def words(self, string):
        return re.split(r'[\s\.\(\)\=\:\-\+\*\/\&\%\^]+', string)

    def guess_string(self, string, r):
        if "=" in string and string.count("=") == 1:
            r = "'" + r + "'"
            return r

    def try_load(self, string, r):
        pys = [ i for i in os.listdir() if i.endswith(".py")]

        words = re.findall(r'(\w+)\s*\(', r)
        if not words:
            words = re.findall(r'(\w+)\s', r)

        for f in pys:
            cprint("-->" + f , "blue")
            
            for m in words:
                try:
                    cmd = "from %s import %s" % (f.split(".")[0], m)
                    self.module(cmd)
                    cprint(" |" + cmd, 'yellow')
                    return r
                except AttributeError:
                    pass

    def try_help(self, words):
        pys = [ i for i in os.listdir() if i.endswith(".py")]
        for f in pys:
            with open(f) as fp:
                funs = []
                fun_name = ''
                for l in fp:
                
                    if len(funs) > 0:
                        if l[0] != ' ':
                            function = ''.join(funs)
                            cprint(function, 'blue')
                            funs = []
                            fun_name = ''
                        else:
                            funs.append(l)
                    
                    if l.startswith("def"):
                        
                        fun_name = l.split("def", 1)[1].split("(")[0].strip()
                        # print(fun_name)
                        if fun_name in words:
                            funs.append(l)
                        else:
                            fun_name = ""


    def load_funcs(self):
        pys = [ i for i in os.listdir() if i.endswith(".py")]
        for f in pys:
            cprint("-->" + f , "blue")
            with open(f) as fp:
                content = fp.read()
                # print(content)
                funcs = []
                classes = []
                attrs = []
                for l in content.split("\n"):
                    fun = re.findall(r'^def\s+(\w+?)\s*\(.+\):', l)
                    if len(fun) >0:
                        funcs.append(fun[0])

                    cl = re.findall(r'^class\s+(\w+)\s*(?:\(\w+\))?\:', l)
                    if cl:
                        classes.append(cl[0])
                    
                    at = re.findall(r'^(\w+?)\s*\=', l)
                    if at:
                        attrs.append(at[0])

                # print(funcs, classes, attrs)
                for m in  (funcs + classes + attrs):
                    cmd = "from %s import %s" % (f.split(".")[0], m)
                    cprint(" |" + cmd, 'yellow')
                    self.module(cmd)

    def parse_setattr(self, string):
        r = string
        l = '_'
        if not re.match(r'[\'"]',string.strip()[0]):
            if "=" in string:
                l, r =string.split("=", 1)
        try:
            res = eval(r, self.sess._attres,self.sess._attres)
            self.sess.add_attr(l.strip(), res)
        except (NameError, SyntaxError) as e:
            r = self.try_load(string, r)
            if not r:
                r = self.guess_string(string, r)
            
            if r is not None:
                string = l + " = " + r
                print(string)

            if r is None:
                raise e
            res = eval(r, self.sess._attres,self.sess._attres)
            self.sess.add_attr(l.strip(), res)


        self.sess.add_input(string)
        return res
    

    def parse_quote(self, string):
        unquote = re.split(r'[\"\'].+?[\"\']', string)
        quote = re.findall(r'[\"\'].+?[\"\']', string)
        f = ''

        searched_unquote = []
        for graph in unquote:
            ws = self.words(graph)
            t = graph
            si = 0
            tm = ''
            for w in ws:
                g = self.sess.search(w)
                
                t = t[:si] + t[si:].replace(w, g, 1)
                si = t.index(w)
                si += 1
            searched_unquote.append(t)

        l = max([searched_unquote, quote], key=lambda x: len(x))
        r = min([searched_unquote, quote], key=lambda x: len(x))
        res = [l[0],]
        for i in range(len(r)):
            res.append(r[i])
            res.append(l[i+1])
        
        return ''.join(res)
    
    def info(self):
        pys = [ i for i in os.listdir() if i.endswith(".py")]
        for f in pys:
            cprint("-->" + f , "blue")
            with open(f) as fp:
                content = fp.read()
                # print(content)
                funcs = []
                classes = []
                attrs = []
                for l in content.split("\n"):
                    fun = re.findall(r'^def\s+(\w+?.+):', l)
                    if len(fun) >0:
                        funcs.append(fun[0])

                    cl = re.findall(r'^class\s+(\w+)\s*(?:\(\w+\))?\:', l)
                    if cl:
                        classes.append(cl[0])
                    
                    at = re.findall(r'^(\w+?)\s*\=', l)
                    if at:
                        attrs.append(at[0])
                for f in funcs:
                    cprint(colored("[Fun] : ","green") + f, "yellow")

                for c in classes:
                    cprint(colored("[Class] : ","red") + c, "yellow")

                for a in attrs:
                    cprint(colored("[Var] : ","blue") + a, "yellow")

    def Parse(self, strings):
        funs = []
        fun_name = ''
        dine_fun = False
        for l in  strings.split("\n"):
            # cprint(l, "yellow")
            if l == "%var":
                for i in self.sess._attres:
                    if i == '__builtins__':continue
                    cprint(i + " =>" + str(self.sess._attres[i]), 'yellow')
                sys.exit(0)
            elif l == "%cl":
                self.sess.clear()
                sys.exit(0)
            elif l == "%load":
                self.load_funcs()
                self.save()
                sys.exit(0)
            elif l == "%info":
                self.info()
                sys.exit(0)

            elif l == "%hist":
                for i,l in enumerate(self.sess._inputs):
                    cprint('%2d' % i + ":" + l, 'green')
                sys.exit(0)

            help_words = re.findall(r'(\w+)\?', l)
            if help_words:
                cprint("-> help", 'yellow')
                self.try_help(help_words)
                sys.exit(0)
            
            if not dine_fun:
                if self.module(l):
                    continue

            if dine_fun:
                # print(l)
                funs.append(l)
            # else:
            # print("... ", l)

            if l.startswith("def"):
                funs.append(l)
                
                fun_name = l.split("def", 1)[1].split("(")[0]
                # print("Define: ",fun_name)
                dine_fun = True
                
            
            if len(funs) > 0:
                if l[0] != ' ' or l.startswith("    return"):
                    function = ''.join(funs)
                    self.repl2(function)
                    self.sess.print_in("define : " + fun_name)
                    funs = []
                    fun_name = ''
                    dine_fun = False
            
                
            else:
                self.sess.print_in(l)
                res = self.repl3(l)
                self.sess.print_out(res)


    
    def repl2(self, string):
        exec(string, self.sess._attres,self.sess._attres)
        self.sess.add_input(string)          

    def repl3(self, string):
        res = self.parse_setattr(string)
        
        return res

    def repl(self, string):
        # if "==" in string:
            # pass
        # elif "=" in string:
            # name, string = string.split("=")
        if string.startswith("%"):
            self.cmd(string)
            return

        if self.module(string):
            return

        string = self.parse_quote(string)
        cprint(string, "green")
        res = self.parse_setattr(string)
        return res

    @classmethod
    def Tree(cls, label="py"):
        s = Sess(label)
        return cls(s)