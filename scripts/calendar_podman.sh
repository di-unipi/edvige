# Run the edvige container
# linking these directories:
# - ./layout to /edvige/layout (read-only)
# - ./scripts to /edvige/scripts (read-only)
# - ./static to /edvige/static (read-only)
# - ./logs to /edvige/logs
# - ./www to /edvige/www
# and ./requirements.txt to /edvige/requirements.deployed.txt (read-only),
# to detect an image built from outdated dependencies.
mkdir -p logs
mkdir -p www

# Skip this run if the previous one is still in progress
exec 9> logs/.calendar.lock
if ! flock -n 9; then
  echo "Skip $(date): previous run still in progress" >> logs/calendar.log
  exit 0
fi

podman run --rm \
  -v "$(pwd)/layout":/edvige/layout:ro,z \
  -v "$(pwd)/scripts":/edvige/scripts:ro,z \
  -v "$(pwd)/static":/edvige/static:ro,z \
  -v "$(pwd)/requirements.txt":/edvige/requirements.deployed.txt:ro,z \
  -v "$(pwd)/logs":/edvige/logs:z \
  -v "$(pwd)/www":/edvige/www:z \
  edvige
