# Build Stage
FROM node:alpine AS builder
LABEL maintainer="@nuooooooo"

WORKDIR /app

# Install dependencies
COPY angular-app/package.json angular-app/package-lock.json /app/angular-app/
RUN npm install --prefix angular-app

# Copy source code and build
COPY . /app
RUN npm run build --prefix angular-app -- --output-path=./dist/out

# Serve Stage
FROM nginx:alpine

# Remove the default nginx static files
RUN rm -rf /usr/share/nginx/html/*

# Copy the built Angular app to the nginx static files directory
COPY --from=builder /app/angular-app/dist/out/browser /usr/share/nginx/html

# Copy the nginx configuration file
COPY ./nginx/nginx.conf /etc/nginx/conf.d/default.conf
