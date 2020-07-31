#!/bin/env bash
# By Lukas Ramm

username=
password=
timestamp=$(date +'%Y-%m-%d')

echo Welcome:
echo 0: clean Podman/ Buildah
echo 1: Buildah
echo 2: Docker

read menu
echo

case $menu in
  0)  # Cleaning Up
      podman container cleanup --all
      podman images cleanup --all
      podman system reset

      echo Space usage of Podman:
      du -h --max-depth 1 .local/
      ;;

  1)  # Buildah
      echo Projects:
      echo 1: Proxy: apt-cacher
      echo 2: Downloader: youtube-dl-server
      echo 3: Downloader: ydl-test
      echo 4: Downloader: ydl-feature
      echo 5: Server: sharry

      read menu
      echo

      case $menu in
        1)  # apt-cacher
            echo starting build: ...
            cd buildah_apt-cacher-ng && git pull
            ./build.sh
            podman tag apt-cacher-ng $username/apt-cacher-ng:latest
            podman tag apt-cacher-ng $username/apt-cacher-ng:$timestamp

            echo push: $username/apt-cacher-ng:latest
            podman push --creds $username:$password $username/apt-cacher-ng:latest
            echo push: $username/apt-cacher-ng:$timestamp
            podman push --creds $username:$password $username/apt-cacher-ng:$timestamp
            cd ~/
            ;;

        2) # youtube-dl-server
            echo starting build: ...
            cd youtube-dl-server/build && git pull
            ./buildah.sh
            podman tag youtube-dl-server $username/youtube-dl-server
            podman tag youtube-dl-server $username/youtube-dl-server:$timestamp

            echo push: $username/youtube-dl-server:latest
            podman push --creds $username:$password $username/youtube-dl-server:latest
            echo push: $username/youtube-dl-server:$timestamp
            podman push --creds $username:$password $username/youtube-dl-server:$timestamp
            cd ~/
            ;;

        3) # youtube-dl-server
            echo starting build: ...
            cd youtube-dl-server/build && git pull
            ./buildah.sh
            podman tag youtube-dl-server ydl-test
            cd ~/
            ;;

        4) # youtube-dl-server
            echo starting build: ...
            cd youtube-dl-server/build && git pull --all && git checkout feature && git pull --all
            ./buildah.sh
            git checkout master
            podman tag youtube-dl-server ydl-feature
            cd ~/
            ;;

        5)  # sharry
            echo starting build: ...
            cd buildah_sharry && git pull

            echo Version?
            read version

            ./build.sh
            podman tag sharry $username/sharry:latest
            podman tag sharry $username/sharry:$version

            echo push: $username/sharry:latest
            podman push --creds $username:$password $username/sharry:latest
            echo push: $username/sharry:$version
            podman push --creds $username:$password $username/sharry:$version
            cd ~/
            ;;
      esac
     ;;
esac

if [ $menu != "0" ]; then
  echo build finished
fi
