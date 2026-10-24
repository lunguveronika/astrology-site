#!/bin/bash
echo "Сборка Docker-образа..."
docker build -t astrolog-site:latest .
echo "Сборка завершена!"