# Queue

Code: `src/shop/queue.py`

Jobs are stored in SQLite rather than a broker: one machine runs everything, and this
keeps the deployment to a single process with nothing else to operate.
