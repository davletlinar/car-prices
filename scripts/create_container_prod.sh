cd ~/car-prices/car-prices-py
git pull;
docker compose down;
docker compose up -d --build;
docker ps;
docker logs -f car-prices-py