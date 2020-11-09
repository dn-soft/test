# docker pull test1236.azurecr.io/testimage
docker login test1236.azurecr.io
echo test1236
echo iOj/573TN0jY+mwIT79Hh3bOICI38O7F
docker pull test1236.azurecr.io/testimage
docker run -p 3000:3000 -d testimage
