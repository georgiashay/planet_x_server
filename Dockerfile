FROM node:stretch-slim

WORKDIR /usr/src/app

COPY ./node_server ./

RUN cd dependencies/pubsub-ws && npm install && npm run build

RUN cd /usr/src/app && npm install 

CMD [ "node", "server.js" ]

EXPOSE 8000

