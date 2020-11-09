# docker pull test1236.azurecr.io/testimage
docker login test1236.azurecr.io
docker pull test1236.azurecr.io/testimage:40
echo ????????????????????????
docker bulid test1236.azurecr.io/testimage:40
docker run -p 3000:3000 -d test1236.azurecr.io/testimage:40
