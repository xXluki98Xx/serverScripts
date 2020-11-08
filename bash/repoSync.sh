#!/bin/bash
# By Lukas Ramm

# Git Repo Sync

#####

# Git URL
url=""

# Arrays
rFolder=()

rSoftware=()
rServiceMuster=()
rsysAdmin=()
rVM=()

#####

echo Willkommen im RepoSync
echo
echo Was wollen Sie machen?
echo 1 - Repos Downloaden"/" erstellen
echo 2 - Repos Aktualisieren

read menu
echo

cd ..

case $menu in
    1)  # Repos Downloaden
        mkdir -p Git-Repos && cd Git-Repos

        for Folder in ${rFolder[@]}
        do
            mkdir -p $Folder

            cd $Folder
            echo clonning now $Folder

            var=r$Folder[@]
            echo
            echo Welcher folgende Repos beinhaltet:
            echo ${!var}
            echo

            for project in ${!var}
            do
                echo "clonning $project"
                git clone $url/$Folder/$project.git
                echo
            done
            cd ..
        done
        ;;

    2)  # Repos Aktualisieren
        cd Git-Repos/
        path=$(pwd)
        gitrepo=$(find . -mindepth 2 -maxdepth 2 -type d)

        for element in ${gitrepo[@]}
        do
            cd $element
            echo "pulling $element"
            git pull
            echo
            cd $path
        done
        ;;
esac