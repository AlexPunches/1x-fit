# CI/CD Workflow Documentation

## Overview

Our CI/CD pipeline consists of two main workflows:

1. **Build and Push** (`build_push.yml`) - Automatically builds and pushes Docker images
2. **Deploy** (`deploy.yml`) - Deploys the bot to production (manually triggered)

## Build and Push Workflow

This workflow is triggered automatically on:
- Push to `main` or `develop` branches
- Creation of tags (releases)
- Pull requests to `main` or `develop` branches

It performs the following actions:
- Builds a Docker image from the `bot` directory
- Tags the image with multiple tags (branch, SHA, latest, semver)
- Pushes the image to Docker Hub
- Runs on both AMD64 and ARM64 architectures

## Deploy Workflow

This workflow can be triggered manually through GitHub's "Run workflow" button. It:
- Pulls the latest Docker image from Docker Hub
- Deploys the bot to the production server
- Uses environment variables stored in GitHub Secrets
- Maintains persistent volumes for data storage

## Deployment Process

To deploy the bot:

1. Make sure your code is pushed to the repository
2. Wait for the build workflow to complete (image is pushed to Docker Hub)
3. Go to the Actions tab in GitHub
4. Select the "Build, Publish and Deploy" workflow
5. Click "Run workflow" 
6. Choose the branch/ref you want to deploy
7. The workflow will deploy the corresponding image to production

## Environment Variables

The deployment requires the following secrets to be configured in GitHub:
- `VM_HOST`: Host address of the deployment server
- `VM_USER`: Username for SSH connection
- `SSH_PRIVATE_KEY`: Private key for SSH authentication
- `DOCKERHUB_USERNAME`: Docker Hub username
- `DOCKERHUB_TOKEN`: Docker Hub access token
- `BOT_ENV_FILE`: Base64-encoded .env file content with bot configuration

## Image Tagging Strategy

Images are tagged using the following strategy:
- Branch name (e.g., `main`, `develop`)
- Pull request number (e.g., `pr-123`)
- Commit SHA (e.g., `main-a1b2c3d`)
- `latest` (for main branch)
- Semantic version (for tags, e.g., `v1.2.3`)