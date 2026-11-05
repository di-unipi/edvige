# Use Python 3.12 on Debian Bookworm as the base image, pinned by digest
# (multi-arch index: amd64, arm/v7, arm64). To update the base image, look up
# the current digest, e.g. with `podman manifest inspect python:3.12-slim-bookworm`.
FROM python:3.12-slim-bookworm@sha256:da54eb86849fe19be7584d8b3f291fcf0c53c196760ab3d70dc6382f681ef9c0

# Set environment variables to avoid user input prompts
ENV DEBIAN_FRONTEND=noninteractive

# Set container to have Europe/Rome timezone
RUN apt-get update && \
    apt-get install -y --no-install-recommends tzdata && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    ln -sf /usr/share/zoneinfo/Europe/Rome /etc/localtime && \
    echo "Europe/Rome" > /etc/timezone

# Create and enter the /edvige directory
WORKDIR /edvige

# Install pinned dependencies (exported from uv.lock)
COPY requirements.txt .
RUN pip3 install --no-cache-dir --require-hashes -r requirements.txt

# Render the calendar when the container starts
CMD ["bash", "scripts/calendar.sh"]
