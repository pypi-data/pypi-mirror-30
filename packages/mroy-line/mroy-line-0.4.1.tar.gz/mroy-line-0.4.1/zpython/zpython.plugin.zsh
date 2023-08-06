
function load_sess(){
    sess_token="$(cat /tmp/session| xargs )"
    if [ -f /tmp/psession/$sess_token.hist ];then
        cat /tmp/psession/$sess_token.hist;
    fi
}

function log(){
    echo $@ >> /tmp/info.error.log;
}

if type compdef &>/dev/null;then
    _callback_from_jedi (){
        log ${words[2,-1]}
        # log $cword
        pre_hist="$(load_sess)"
        source="${words[2,-1]}"
        res=$(cat <<EOF | python
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

# with open("/tmp/info.error.log", "w") as fp:
    # for c in coms:
        # print(c.name, file=fp)
#    print("============")
#    print(source)

for c in coms:
    print(c.complete)
EOF
)
        # echo $res > /tmp/info.res.log
        if [[ $res != "" ]];then
            line=$(echo $res)
            compset -P '*'
            compadd -Q  $(echo $res)
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
