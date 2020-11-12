FROM node:12
WORKDIR /app

COPY . .

RUN npm i -g pm2
RUN npm i
RUN chmod 774 deploy.sh

EXPOSE 3000

CMD [ "pm2-runtime", "start", "./bin/www"]

ENTRYPOINT ["/home/azureuserDoc/deploy.sh"]