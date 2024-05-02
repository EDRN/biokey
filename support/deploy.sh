#!/bin/sh -e
#
# Deploy onto edrn-docker.
#
# Expect to run this in either /usr/local/labcas/biokey/dev or in
# /usr/local/labcas/biokey/ops.

if [ ! -f "docker-compose.yaml" -o ! -f ".env" ]; then
    echo "🚨 Run this from the either the dev or ops directories on edrn-docker for BioKey" 1>&2
    echo "You should have docker-compose.yaml and .env files in the current directory" 1>&2
    exit 1
fi

project_name=biokey-`basename ${PWD}`
echo "📽️ Using project name ${project_name}" 1>&2

compose() {
    docker compose --project-name ${project_name} "$@"
}

echo "🛑 Stopping and removing any existing containers and services"
compose down --remove-orphans --volumes

compose run --rm --volume ${PWD}/docker-data:/mnt --no-TTY --entrypoint /bin/rm db -rf /mnt/postgresql || :
[ -d docker-data ] || mkdir docker-data
for sub in media postgresql; do
    rm -rf docker-data/$sub
    mkdir docker-data/$sub
done

echo "🪢 Pulling latest images"
compose pull --quiet

echo "🚢 Creating containers and starting composition in detached mode" 1>&2
compose up --detach --quiet-pull --remove-orphans

echo "⏱️ Waiting a ½ minute for things to stabilize…" 1>&2
sleep 30

echo "❌ Destroying any existing biokey database" 1>&2
compose exec db dropdb --force --if-exists --username=postgres biokey
echo "🫄 Creating a new empty biokey database"
compose exec db createdb --username=postgres --encoding=UTF8 --owner=postgres biokey
echo "🦆 Applying DB structure"
compose exec app /app/src/manage.py migrate
echo "🌸 Blooming initial content and settings"
compose exec app /app/src/manage.py biokey_bloom

echo "🎉 Done!"
exit 0
