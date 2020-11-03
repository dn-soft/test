FROM node:12
WORKDIR /app

COPY . .

RUN npm i -g pm2
RUN npm i

EXPOSE 3000

CMD [ "pm2-runtime", "start", "./bin/www"]