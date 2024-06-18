#!/bin/zsh
source scripts/version.sh
mkdir -p sql
if [[ ! -v FASTAPI_ENV ]];
then
    export FASTAPI_ENV=dev
fi
if [[ -v FASTAPI_ENV && $FASTAPI_ENV =~ ^(dev|preproduction|production)$ ]];
then
    cat scripts/templates/.env.$FASTAPI_ENV.example > .env
fi
echo "SECRET_KEY_JWT=`openssl rand -hex 32`" >> .env
case $@ in
    "aws")
        sed -e "s/\[APP_VERSION\]/$APP_VERSION/g" -e "s/\[FASTAPI_ENV\]/$FASTAPI_ENV/g" scripts/templates/.env.aws.example >> .env
        sed -e "s|\[HTTP_PROXY\]|http://eu1.proxy.cloud.ad:3128|g" scripts/templates/Dockerfile.aws.example > Dockerfile
        ;;
    "docker")
        sudo rm -rf ../postgres_data
        password_db=`date +%s | sha256sum | base64 | head -c 32 ; echo`
        cat scripts/templates/.env.example >> .env
        if [[ -v STUDIO_ID ]];
        then
            sed -i '' -e "s/\[UID_STUDIO\]/$STUDIO_ID/g" -e "s/\[UVICORN_PORT\]/8000/g" .env
        else
            sed -i '' -e "/.*\[UID_STUDIO\].*/d" .env
        fi
        if [[ -v FASTAPI_ENV ]];
        then
            sed -i '' -e "s/\[FASTAPI_ENV\]/$FASTAPI_ENV/g" .env
        else
            sed -i '' -e "/.*\[FASTAPI_ENV\].*/d" .env
        fi
        if [[ -v HTTP_PROXY ]];
        then
            sed -e "s|\[HTTP_PROXY\]|$HTTP_PROXY|g" scripts/templates/Dockerfile.example > Dockerfile
        else
            sed -e "/.*\[HTTP_PROXY\].*/d" scripts/templates/Dockerfile.example > Dockerfile
        fi
        sed -i '' -e "s/\[APP_SOURCE\]/docker/g" -e "s/\[APP_VERSION\]/$APP_VERSION/g" -e "s/\[PASSWORD_DB\]/$password_db/g" -e "s/\[DATABASE_USER\]/postgres/g" -e "s/\[SERVER_DB\]/db/g" -e "s/\[DATABASE_DB\]/dbo/g" .env
        sed -e "s/\[PASSWORD_DB\]/$password_db/g" scripts/templates/docker-compose.example > docker-compose.yml
        docker-compose build || exit 1
        echo -e "\nYou can now use the docker-compose commands."
        echo -e "\t\033[0;32mdocker-compose up -d\033[0m"
        ;;
    "local")
        cat  scripts/templates/.env.example >> .env
        if [[ -v STUDIO_ID ]];
        then
            sed -i '' -e "s/\[UID_STUDIO\]/$STUDIO_ID/g" -e "s/\[UVICORN_PORT\]/8000/g" .env
        else
            sed -i '' -e "/.*\[UID_STUDIO\].*/d" .env
        fi
        if [[ -v FASTAPI_ENV ]];
        then
            sed -i '' -e "s/\[FASTAPI_ENV\]/$FASTAPI_ENV/g" .env
        else
            sed -i '' -e "/.*\[FASTAPI_ENV\].*/d" .env
        fi
        sed -i '' -e "s/\[APP_SOURCE\]/local/g" -e "s/\[APP_VERSION\]/$APP_VERSION/g" -e "/.*DATABASE.*/d" .env
        if ! pip freeze | diff requirements.txt -;
        then
            pip install -r requirements.txt
        fi
        echo -e "\nYou can now use the uvicorn commands."
        echo -e "\t\033[0;32muvicorn app.main:app --reload\033[0m"
        ;;
    *)
        rm .env
        echo "Run this script with valid arg : aws | docker | local"
        exit 1
esac
