# Adding docker image to EC@



1. Create a repository on ECR
2. Build the docker image `docker build --platform linux/amd64 -t create-bayesian-trace .`
3. Tag it in preparation for push `docker tag [imageid] [ecr-repo-aws-region-docker-tag]`
4. login to aws ecr `aws ecr get-login-password --region ap-southeast-2 | docker login --username AWS --password-stdin XXXXXX12345.dkr.ecr.ap-southeast-2.amazonaws.com/mattsrepo`
5. `docker push XXXXXX12345.dkr.ecr.[aws-region].amazonaws.com/mattsrepo:create-bayesian-trace`

