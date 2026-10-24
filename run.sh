#!/bin/bash
echo "Запуск контейнера..."
docker stop astrolog-site 2>/dev/null || true
docker rm astrolog-site 2>/dev/null || true
docker run -d -p 5000:5000 --name astrolog-site --restart always astrolog-site:latest
echo "Сайт запущен! Откройте http://localhost:5000"