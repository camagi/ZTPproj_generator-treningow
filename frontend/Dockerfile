FROM node:20-alpine AS build

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/. ./

ARG NEXT_PUBLIC_API_URL=/api
ARG NEXT_PUBLIC_STATIC_URL=/exercises-static
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
ENV NEXT_PUBLIC_STATIC_URL=${NEXT_PUBLIC_STATIC_URL}

RUN npm run build

FROM nginx:alpine

COPY --from=build /app/out /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
