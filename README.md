# Pythonz

## Deployment

### Server Deployment

The site should be running already on the server - webtech-03.napier.ac.uk

If it's not (or it breaks to the extent it needs a restart), then run the command `gunicorn3 --worker-class eventlet -w 1 main:app --bind 127.0.0.1:8000` from the site's directory. If that's still not working, restart nginx, which passes through the traffic.

Be sure to kill the old process first, which is running in the background using `nohup ... &` and can be viewed by running `jobs`.

### Local Deployment

Local deployment is a bit of an involved process, as sockets are used. For a limited functionality (which may break due to lack of socket support), then `python3 main.py` can be used.

For a more complete deployment, install `gunicorn3` (via `apt`) and `eventlet` (via `pip3`), and then run the command above.
