# Run the edvige container
# linking these directories:
# - ./layout to /edvige/layout (read-only)
# - ./scripts to /edvige/scripts (read-only)
# - ./static to /edvige/static (read-only)
# - ./logs to /edvige/logs
# - ./www to /edvige/www
mkdir -p logs
mkdir -p www
podman run --rm \
  -v "$(pwd)/layout":/edvige/layout:ro,z \
  -v "$(pwd)/scripts":/edvige/scripts:ro,z \
  -v "$(pwd)/static":/edvige/static:ro,z \
  -v "$(pwd)/logs":/edvige/logs:z \
  -v "$(pwd)/www":/edvige/www:z \
  edvige
