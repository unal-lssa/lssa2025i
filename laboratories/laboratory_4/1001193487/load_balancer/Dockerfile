# Use the official Nginx image from Docker Hub
FROM nginx:alpine

# Copy custom Nginx configuration file if you have one
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80
EXPOSE 80

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]