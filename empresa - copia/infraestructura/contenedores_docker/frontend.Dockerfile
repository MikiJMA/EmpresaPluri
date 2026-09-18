FROM node:24-alpine AS build
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
# La interfaz usa /api del mismo origen a través de Nginx.
ENV VITE_API_URL=/
RUN npm run lint && npm run build

FROM nginx:stable-alpine
COPY infraestructura/contenedores_docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
