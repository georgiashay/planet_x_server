FROM node:stretch-slim

WORKDIR /usr/src/app

COPY ./node_server ./

RUN npm install 

CMD [ "node", "server.js" ]

EXPOSE 8000

