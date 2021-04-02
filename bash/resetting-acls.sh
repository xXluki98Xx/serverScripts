#!/bin/bash

# dir loops: https://stackoverflow.com/questions/2107945/how-to-loop-over-directories-in-linux
# acls : https://www.commandlinefu.com/commands/view/4281/copy-acl-of-one-file-to-another-using-getfacl-and-setfacl

oldPath=$(pwd)

# Storage disk = ('/dev/test' '/srv/')
rFolder=('')

# loop for multiple Directories
for Folder in ${rFolder[@]}
do
    cd $Folder

    # looping over the dirs
    for curDir in ${Folder}/*/
    do
        # remove the trailing "/"
        dir=${curDir%*/}
        echo "changing directory ${curDir}"

        # cuts everything after the final "/"
        # pipe current conf to set function
        getfacl "${dir##*/}" | setfacl -R --set-file=- "${dir##*/}"
    done
done
cd $oldPath