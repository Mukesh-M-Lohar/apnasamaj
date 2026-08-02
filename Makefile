.PHONY: help local dev seed deploy-aws deploy-azure clean

# Environment Variables
AWS_REGION ?= us-east-1
AWS_ACCOUNT_ID ?= 123456789012
AWS_ECR_REPO ?= apnasamaj-api
AZURE_ACR_NAME ?= apnasamajacr
AZURE_IMAGE_NAME ?= apnasamaj-api

help:
	@echo "ApnaSamaj Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make local         - Copy .env.example to .env and start local Docker compose stack (Backend only)"
	@echo "  make run-docker    - Start the ENTIRE ecosystem (DB, Redis, API, Web, Mobile) via docker-compose"
	@echo "  make dev           - Run the FastAPI backend locally with uvicorn hot-reload"
	@echo "  make mobile        - Start the Expo React Native mobile app"
	@echo "  make web           - Start the Next.js admin dashboard locally"
	@echo "  make seed          - Generate dummy data in the local database"
	@echo "  make deploy-aws    - Build and deploy Docker image to AWS ECR/ECS"
	@echo "  make deploy-azure  - Build and deploy Docker image to Azure ACR/Container Apps"
	@echo "  make clean         - Stop and remove local Docker containers"

# --- LOCAL DEVELOPMENT ---

.env:
	@if [ ! -f .env ]; then \
		echo "Creating .env from .env.example..."; \
		cp .env.example .env; \
	fi

local: .env
	@echo "Starting backend local environment (Postgres, Redis, API)..."
	docker-compose up -d db redis minio api

run-docker: .env
	@echo "Starting the ENTIRE ecosystem in Docker..."
	docker-compose up --build

dev: .env
	@echo "Starting FastAPI development server..."
	uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000

mobile:
	@echo "Starting Expo Mobile App..."
	cd apps/mobile && npm install && npx expo start

web:
	@echo "Starting Next.js Web Admin Dashboard..."
	cd apps/web && npm install && npm run dev

seed:
	@echo "Seeding local database with dummy data..."
	PYTHONPATH=. python scripts/seed.py

clean:
	@echo "Stopping local environment..."
	docker-compose down

# --- AWS DEPLOYMENT ---

deploy-aws:
	@echo "Logging into AWS ECR..."
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
	@echo "Building Docker image..."
	docker build -t $(AWS_ECR_REPO):latest .
	@echo "Tagging Docker image..."
	docker tag $(AWS_ECR_REPO):latest $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(AWS_ECR_REPO):latest
	@echo "Pushing Docker image to ECR..."
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(AWS_ECR_REPO):latest
	@echo "Updating AWS ECS Service (Ensure you replace cluster/service names)..."
	# aws ecs update-service --cluster ApnaSamajCluster --service ApnaSamajApi --force-new-deployment --region $(AWS_REGION)
	@echo "AWS Deployment commands executed!"

# --- AZURE DEPLOYMENT ---

deploy-azure:
	@echo "Logging into Azure CLI (if needed, run 'az login' manually first)..."
	@echo "Logging into Azure Container Registry..."
	az acr login --name $(AZURE_ACR_NAME)
	@echo "Building Docker image..."
	docker build -t $(AZURE_ACR_NAME).azurecr.io/$(AZURE_IMAGE_NAME):latest .
	@echo "Pushing Docker image to ACR..."
	docker push $(AZURE_ACR_NAME).azurecr.io/$(AZURE_IMAGE_NAME):latest
	@echo "Updating Azure Container App (Ensure you replace resource-group/app-name)..."
	# az containerapp update --name ApnaSamajApp --resource-group ApnaSamajGroup --image $(AZURE_ACR_NAME).azurecr.io/$(AZURE_IMAGE_NAME):latest
	@echo "Azure Deployment commands executed!"
