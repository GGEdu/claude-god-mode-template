# Build de los docs (VitePress) → nginx, para servir INTERNO (LAN/Tailscale).
# NO usar GitHub Pages en repos privados/homelab: en cuenta personal Pages es
# PÚBLICO aunque el repo sea privado. Contexto de build = docs/
FROM node:20-alpine AS build
# git: VitePress lo invoca para la marca `lastUpdated` de cada página.
RUN apk add --no-cache git
WORKDIR /docs
COPY package.json package-lock.json* ./
RUN npm ci || npm install
COPY . .
RUN npm run docs:build

FROM nginx:alpine
COPY --from=build /docs/.vitepress/dist /usr/share/nginx/html
COPY deploy-internal/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
