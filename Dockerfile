# Use Node.js 17.9.0 on Debian Bullseye as the base image
FROM node:17.9.0-bullseye

# Set environment variables to avoid user input prompts
ENV DEBIAN_FRONTEND=noninteractive

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

# Install a web server
RUN npm install -g http-server

# Copy the whole project to the container
COPY . .

# Run the script to generate static content
RUN npm run calendar

# Serve the www directory
EXPOSE 8080

# Start the web server
CMD ["http-server", "./www"]
