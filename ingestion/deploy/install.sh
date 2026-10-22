#!/usr/bin/env bash
# install.sh - set up the collector on a fresh Ubuntu 24.04 VM (run on the VM as ubuntu).
# Expects the code at ~/fyp (copied with rsync from the development machine).
set -euo pipefail
APP=/home/ubuntu/fyp
DATA=/home/ubuntu/fyp-data/bronze

sudo apt-get update -q
sudo apt-get install -y -q python3-venv zstd

# 1 GB swap so that a 1 GB VM survives memory spikes (skipped if swap already exists)
if [ -z "$(swapon --show)" ]; then
  sudo fallocate -l 1G /swapfile
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
  echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi

python3 -m venv "$APP/.venv"
"$APP/.venv/bin/pip" install -q --upgrade pip
"$APP/.venv/bin/pip" install -q -r "$APP/ingestion/requirements.txt"
mkdir -p "$DATA"

sudo cp "$APP"/ingestion/deploy/*.service "$APP"/ingestion/deploy/*.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now gtfs-rt-collector.service gtfs-rt-pack.timer \
  fyp-static.timer fyp-weather-forecast.timer fyp-weather-warning.timer fyp-ridership.timer
systemctl --no-pager status gtfs-rt-collector.service | head -n 5
