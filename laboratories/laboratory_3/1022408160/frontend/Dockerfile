FROM nginx:1.25-alpine

# Set working directory (optional, but good practice)
WORKDIR /usr/share/nginx/html

# Remove default nginx welcome page
RUN rm -f index.html

# Copy your static frontend files into the nginx webroot
COPY index.html .
COPY script.js .
COPY style.css .

# Nginx default port is 80
EXPOSE 80

# Default command is to start nginx
CMD ["nginx", "-g", "daemon off;"]