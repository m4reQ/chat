FROM node:25-alpine

WORKDIR /frontend

COPY ./package*.json /frontend

RUN npm install

COPY . /frontend

CMD ["npm", "start"]