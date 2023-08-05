function cdd_match {
    cddmatch=$(~/cdd/cdd $1 | head -1)
}

function cdd_add {
    ~/cdd/cdd -a
}

function cdd_del {
    ~/cdd/cdd -d $1
}

function cd {
    if [[ $# == 0 ]]; then
        # no argument used
        command cd
        return 0
    fi

    if [[ $# == 1 ]] && [[ -d "$1" ]]; then
        # argument is a directory in current directory
        command cd "$1"

        # add directory to the database
        cdd_add $PWD

        # and that's all
        return 0
    fi

    # assume argument $1 is a pattern
    cdd_match $1
    if [[ -d "$cddmatch" ]]; then
        command cd $cddmatch
    else
        cdd_del "$cddmatch"
    fi
}
