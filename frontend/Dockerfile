# ETAPA 1: Construcción (Node)
FROM node:20-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# ETAPA 2: Producción (Nginx)
FROM nginx:alpine
# Copiamos la carpeta /dist que generó Vite hacia la carpeta pública de Nginx
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80

# Nginx arranca por defecto, no necesitamos CMD