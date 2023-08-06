import os, sys
from argparse import ArgumentParser
from P.lang import LangTree
from types import  FunctionType

Arger = ArgumentParser()
# Arger.add_argument("-s", "--session", default=False, action='store_true', help="update proxy...")
Arger.add_argument("shell", type=str, nargs="*", help="run")
Arger.add_argument("-s", "--switch", default=None, help="set a session")
Arger.add_argument("-F", "--File", default=False, action='store_true', help="if set , will put args as file or filepath.")
Arger.add_argument("-P", "--no-pre", default=True, action='store_false', help="if set , will not load *.pycc file by auto.")
Arger.add_argument("-f", "--test-function", default=None, help="use this to test function : cmd.py -f fun args1 args2 args3 ")




def run():
    
    args = Arger.parse_args()

    if args.switch:
        with open("/tmp/session", "w") as fp:
            fp.write(args.switch)
            sys.exit(0)        
    

    
    if os.path.exists("/tmp/session"):
        token = "test"
        with open("/tmp/session") as fp:
            token = fp.readline().strip()
            l = LangTree.Tree(token)

            # w = ' '.join(args.shell)
            # w = sys.stdin.read()
            # print(sys.argv)

            
            if not args.shell:
                print("From Stdin:")
                w = sys.stdin.read()
                if args.test_function:
                    l.Test(args.test_function, w, pre_load= args.pre_load)
                    l.sess.save()
                    sys.exit(0)
                else:
                    l.Parse('tmp="""{}"""'.format(w), pre_load= args.pre_load)
                    l.sess.save()
                    sys.exit(0)
            else:
                w = ' '.join(args.shell)
            
                if args.test_function:
                    l.Test(args.test_function, args.shell, tp=args.File)
                    l.sess.save()
                    sys.exit(0)

            l.Parse(w)
            l.sess.save()

if __name__ == "__main__":
    run()
