export MOUNTPOINT="$HOME/PycharmProjects/survey-processing/vol"
DOCKER_BUILDKIT=1 docker build --platform amd64 -t sthv/survay-processing-cxm:latest .
#docker run --rm -p 0.0.0.0:4777:4777  -p 0.0.0.0:5777:5777 --tty -v $MOUNTPOINT:/vol --env HASURA_GQL_ENDPOINT=http://84.201.156.249:8080/v1/graphql  --name survey-proc-service sthv/survay-processing-cxm

docker tag sthv/survay-processing-cxm cr.yandex/crpfskvn79g5ht8njq0k/contextmachine.survey:latest
docker push cr.yandex/crpfskvn79g5ht8njq0k/contextmachine.survey:latest