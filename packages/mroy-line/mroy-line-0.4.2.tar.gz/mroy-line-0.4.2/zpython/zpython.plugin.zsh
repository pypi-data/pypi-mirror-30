
function load_sess(){
    sess_token="$(cat /tmp/session| xargs )"
    if [ -f /tmp/psession/$sess_token.hist ];then
        cat /tmp/psession/$sess_token.hist;
    fi
}


if type compdef &>/dev/null;then
    _callback_from_jedi (){

        # log $cword
        pre_hist="$(load_sess)"
        source="${words[2,-1]}"
        res=$(cat <<EOF | python3
import jedi,sys
source="""$pre_hist\n$source"""
lines = source.split("\n")
line_len = len(lines)
column_len = len(lines[-1])
script = None
try:
    script = jedi.Script(source, line_len, column_len)
    coms = script.completions()
except IndexError:
    print("")
    sys.exit(0)

if not script:
   print()
   sys.exit(0)

for c in coms:
    print(c.complete)
EOF
)
        if [[ $res != "" ]];then
            line=$(echo $res)
            compset -P '*'
            compadd -Q %hist %cl %var %info $(echo $res)
        fi
    }
    compdef _callback_from_jedi rp;
elif type compctl &>/dev/null; then
    _callback_from_jedi (){
        local cword line point words si
        read -Ac words
        read -cn cword
        let cword-=1
    }
fi
