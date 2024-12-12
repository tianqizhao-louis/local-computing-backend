# Deploy

## Cloud Run

```bash
docker build --platform=linux/amd64 -t breeder-service -f ./breeder-service/prod.Dockerfile ./breeder-service/

docker tag [image-id] us-east1-docker.pkg.dev/prime-victory-437119-p7/microservices/breeder:[tag]

docker push us-east1-docker.pkg.dev/prime-victory-437119-p7/microservices/breeder:[tag]
```

Helpers:

```bash
gcloud auth configure-docker \
    us-east1-docker.pkg.dev
```

## GCP VM (Deprecated)

deploy to gcp (deprecated):

make sure you have `prod.env`

```bash
./production_build.sh
```
