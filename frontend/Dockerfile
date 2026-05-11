# Build stage
FROM node:20-alpine AS build
WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Set build arguments
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

# Build app
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
# Copy built assets to Nginx
COPY --from=build /app/dist /usr/share/nginx/html
# Copy custom nginx config if needed (or just use default and map it in compose)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
