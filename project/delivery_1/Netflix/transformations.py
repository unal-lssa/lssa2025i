def generate_frontend(name, backend):
    
    path = f'skeleton/{name}'
    os.makedirs(path, exist_ok=True)

    with open(os.path.join(path, 'package.json'), 'w') as f:
        f.write(textwrap.dedent("""
            {
                "name": "client",
                "private": true,
                "version": "0.0.0",
                "type": "module",
                "scripts": {
                    "build": "tsc -b && vite build",
                    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
                    "preview": "vite preview"
                },
                "dependencies": {
                    "@headlessui/react": "^2.1.2",
                    "@heroicons/react": "^2.1.5",
                    "@hookform/resolvers": "^3.9.0",
                    "@paypal/react-paypal-js": "^8.5.0",
                    "@reduxjs/toolkit": "^2.2.7",
                    "@stripe/react-stripe-js": "^2.8.0",
                    "@stripe/stripe-js": "^4.3.0",
                    "@types/crypto-js": "^4.2.2",
                    "axios": "^1.7.3",
                    "crypto-js": "^4.2.0",
                    "dotenv": "^16.4.5",
                    "hls.js": "^1.5.14",
                    "react": "^18.3.1",
                    "react-dom": "^18.3.1",
                    "react-hook-form": "^7.52.2",
                    "react-player": "^2.16.0",
                    "react-redux": "^9.1.2",
                    "react-router-dom": "^6.26.0",
                    "react-swipeable": "^7.0.1",
                    "tailwind-scrollbar-hide": "^1.1.7",
                    "zod": "^3.23.8"
                }
            }
            """
        ))

    with open(os.path.join(path, 'Dockerfile'), 'w') as f:
        f.write(textwrap.dedent("""
            # Stage 1: Build the Vite application
            FROM node:16-alpine AS build

            WORKDIR /app
            COPY package*.json ./
            RUN npm install
            COPY . .
            RUN npm run build

            # Stage 2: Serve the Vite application with nginx
            FROM nginx:alpine

            # Copy the built files from the previous stage
            COPY --from=build /app/dist /usr/share/nginx/html

            # Copy the custom Nginx configuration
            COPY nginx.conf /etc/nginx/conf.d/default.conf

            EXPOSE 80

            CMD ["nginx", "-g", "daemon off;"]
            """
        ))

def apply_transformations(model):

    components = {}

    for e in model.elements:
        if e.__class__.__name__ == 'Component':
            components[e.name] = e.type
            if e.type == 'frontend ':
                generate_frontend(e.name)