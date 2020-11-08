#!/bin/bash
docker-compose down

    git add .
    git add -A

        git commit -m "Automatic Backup @ $(date)"

    git push origin master

docker-compose up -d