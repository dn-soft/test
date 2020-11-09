# docker pull test1236.azurecr.io/testimage
sudo docker login test1236.azurecr.io
sudo echo test1236
sudo echo iOj/573TN0jY+mwIT79Hh3bOICI38O7F
sudo docker pull test1236.azurecr.io/testimage
sudo docker build --tag testimage 
sudo docker run -p 3000:3000 -d testimage:0.3
