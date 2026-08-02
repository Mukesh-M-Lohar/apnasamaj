# Cloud Deployment

ApnaSamaj provides out-of-the-box Make commands to streamline deploying the containerized backend to AWS and Azure.

## AWS Deployment (ECR / ECS)

To deploy to Amazon Web Services:
1. Ensure the `aws-cli` is installed and you are logged in.
2. Edit the variables at the top of your `Makefile` to match your AWS Region and ECR Repo name.
3. Run:
```bash
make deploy-aws
```
This builds your FastAPI docker image, tags it securely, and pushes it directly to your AWS Elastic Container Registry.

## Azure Deployment (ACR / Container Apps)

To deploy to Microsoft Azure:
1. Ensure the `az-cli` is installed and run `az login`.
2. Edit the variables at the top of your `Makefile` matching your Azure Container Registry (ACR).
3. Run:
```bash
make deploy-azure
```
This builds and pushes the image directly to Azure ACR.
