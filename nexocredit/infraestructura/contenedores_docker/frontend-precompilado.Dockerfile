# Alternativa local: ejecutar lint y Vite con VITE_API_URL=/ antes de construir.
# No descarga dependencias npm ni modifica la validacion TLS.
FROM nginx:stable-alpine
COPY infraestructura/contenedores_docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY frontend/dist /usr/share/nginx/html
EXPOSE 80
