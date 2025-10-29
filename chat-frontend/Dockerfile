# main dir: /frontend
# dist dir: /frontend/dist

FROM node:25-alpine AS builder
WORKDIR /frontend
COPY ./package*.json /frontend
RUN npm install
COPY . /frontend
RUN npm run build

FROM nginx:alpine
RUN rm -rf /usr/share/nginx/html/*
COPY --from=builder /frontend/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]