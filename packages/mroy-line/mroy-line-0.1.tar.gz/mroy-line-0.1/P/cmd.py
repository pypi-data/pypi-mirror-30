import os, sys
from argparse import ArgumentParser
from P.lang import LangTree
from types import  FunctionType

Arger = ArgumentParser()
# Arger.add_argument("-s", "--session", default=False, action='store_true', help="update proxy...")
Arger.add_argument("shell", type=str, nargs="*", help="run")
Arger.add_argument("-s", "--switch", default=None, help="set a session")
Arger.add_argument("-a", "--args", nargs="*", help="pass args")




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
            else:
                w = ' '.join(args.shell)
            
            l.Parse(w)
            l.sess.save()

if __name__ == "__main__":
    run()
