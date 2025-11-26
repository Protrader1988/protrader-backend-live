#!/bin/bash
echo "Starting worker scheduler..."
python workers/paper_trader.py &
python workers/news_worker.py &
wait
