# Run the edvige container
# linking these directories:
# - ./layout to /home/edvige/layout
# - ./logs to /home/edvige/logs
# - ./scripts to /home/edvige/scripts
# - ./static to /home/edvige/static
# - ./www to /home/edvige/www
mkdir -p logs
mkdir -p www
podman run --rm \
  -v "$(pwd)/layout":/edvige/layout:Z \
  -v "$(pwd)/logs":/edvige/logs:Z \
  -v "$(pwd)/scripts":/edvige/scripts:Z \
  -v "$(pwd)/static":/edvige/static:Z \
  -v "$(pwd)/www":/edvige/www:Z \
  edvige
