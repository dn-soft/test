# sudo docker login test1236.azurecr.io
sudo docker stop `docker ps -a -q`
sudo docker rm `docker ps -qa`
sudo export num=$RELEASE_ARTIFACTS__PTEST_BUILDNUMBER
sudo docker pull test1236.azurecr.io/testimage:$RELEASE_ARTIFACTS__PTEST_BUILDNUMBER
sudo docker run -p 3000:3000 -d test1236.azurecr.io/testimage:$RELEASE_ARTIFACTS__PTEST_BUILDNUMBER

