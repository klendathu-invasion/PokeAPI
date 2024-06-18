#!/bin/bash
case $@ in
    "docker")
        docker-compose down
        yes | docker system prune -a
        yes | rm ../log/logfile.log sql/*.sql Dockerfile .env docker-compose.yml
        sudo rm -rf ../postgres_data
        ;;
    "local")
        rm .env
        ;;
    *)
        echo "Run this script with valid arg : docker | local"
        exit 1
esac
