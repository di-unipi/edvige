# Use Python 3.12 on Debian Bookworm as the base image
FROM python:3.12-slim-bookworm

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
