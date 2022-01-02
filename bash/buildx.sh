#!/bin/env bash
# By Lukas Ramm

username=
password=
timestamp=$(date +'%Y%m%d')

docker login --username $username --password $password

echo Welcome:
# echo 0: clean Podman/ Buildah
echo 1: buildx
# echo 2: Docker

read menu
echo

case $menu in
  0)  # Cleaning Up
    #   podman container cleanup --all
    #   podman images cleanup --all
    #   podman system reset
    #   podman rmi $(podman images --noheading --format "table {{.ID}}")

    #   echo Space usage of Podman:
    #   du -h --max-depth 1 .local/
      ;;

  1)  # Buildah
      echo Projects:
      echo 1: Automatic: apt-cacher-ng
      echo 2: Automatic: youtube-dl-server
      echo 3: manually: apt-cacher-ng
      echo 4: manually: youtube-dl-server
    #   echo 5: Server: sharry

      read menu
      echo

      case $menu in
        1)  # automatic apt-cacher-ng
            docker buildx build \
                --platform linux/amd64,linux/arm64 \
                -t lramm/apt-cacher-ng:latest \
                -t lramm/apt-cacher-ng:$timestamp \
                --push \
                https://raw.githubusercontent.com/xXluki98Xx/container_apt-cacher-ng/master/Dockerfile
            ;;

        2) # automatic youtube-dl-server
            docker buildx build \
                --platform linux/amd64,linux/arm64 \
                -t lramm/your-dl-server:latest \
                -t lramm/your-dl-server:$timestamp \
                --push \
                https://raw.githubusercontent.com/xXluki98Xx/your-dl-server/main/Dockerfile
            ;;

        3)  # manually apt-cacher-ng
            echo "please enter tag: "
            read tag

            docker buildx build \
                --platform linux/amd64,linux/arm64 \
                -t lramm/apt-cacher-ng:latest \
                -t lramm/apt-cacher-ng:$tag \
                --push \
                https://raw.githubusercontent.com/xXluki98Xx/container_apt-cacher-ng/master/Dockerfile
            ;;

        4) # automatic youtube-dl-server
            echo "please enter tag: "
            read tag

            docker buildx build \
                --platform linux/amd64,linux/arm64 \
                -t lramm/your-dl-server:latest \
                -t lramm/your-dl-server:$tag \
                --push \
                https://raw.githubusercontent.com/xXluki98Xx/your-dl-server/main/Dockerfile
            ;;

        5)  # sharry
            echo starting build: ...
            cd buildah_sharry && git pull

            version=$(curl -sL https://api.github.com/repos/eikek/sharry/releases/latest | jq -r ".tag_name" | cut -d "/" -f2)

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

docker logout