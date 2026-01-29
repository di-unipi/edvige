# Use Node.js 17.9.0 on Debian Bullseye as the base image
FROM node:17.9.0-bullseye

# Set environment variables to avoid user input prompts
ENV DEBIAN_FRONTEND=noninteractive

# Set container to have Europe/Rome timezone
RUN ln -sf /usr/share/zoneinfo/Europe/Rome /etc/localtime && \
    echo "Europe/Rome" > /etc/timezone

# Update the package list and install prerequisites
RUN apt-get update && \
    apt-get install -y curl software-properties-common build-essential

# Update package list and install necessary packages
RUN apt-get update && \
    apt-get install -y python3.9 python3-pip curl && \
    apt-get clean

# Create and enter the /edvige directory
WORKDIR /edvige

# Install dependencies
COPY package.json package-lock.json ./
COPY requirements.txt .
RUN npm ci && \
    pip3 install -r requirements.txt

# Run npm run calendar when the container starts
CMD ["npm", "run", "calendar"]
