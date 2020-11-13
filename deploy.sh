# sudo docker login test1236.azurecr.io
# sudo docker stop `docker ps -a -q`
# sudo docker rm `docker ps -qa`

# sudo docker pull test1236.azurecr.io/testimage:latest
# sudo docker run -p 3000:3000 -d test1236.azurecr.io/testimage:latest
docker pull test1236.azurecr.io/testimage
