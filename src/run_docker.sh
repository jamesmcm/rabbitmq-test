#! /bin/sh
rm -f ../input/finding.csv;
docker-compose up --build --force-recreate --renew-anon-volumes;
sudo docker-compose down;
rm -f ../input/finding.csv;
