# Deployment Guide

## Overview

This guide explains how to deploy the 1x-fit bot to production.

## Prerequisites

Before deploying, ensure that:

1. Your code is committed and pushed to the repository
2. The build workflow has successfully completed (image pushed to Docker Hub)
3. You have access to the GitHub repository with appropriate permissions

## Deployment Steps

### 1. Automatic Build Process

Every commit to `main` or `develop` branches triggers an automatic build process:

1. A Docker image is built from the `bot` directory
2. The image is tagged appropriately (with branch name, commit SHA, etc.)
3. The image is pushed to Docker Hub

Wait for this process to complete before proceeding with deployment.

### 2. Manual Deployment

To deploy the bot:

1. Navigate to the **Actions** tab in the GitHub repository
2. Find the **"Build, Publish and Deploy"** workflow in the left sidebar
3. Click the **"Run workflow"** dropdown button
4. Select the branch/ref you want to deploy (typically `main`)
5. Click **"Run workflow"** to start the deployment

The deployment workflow will:
- Pull the latest Docker image from Docker Hub
- Stop the current bot container
- Start a new container with the updated image
- Maintain persistent data using Docker volumes

## Deployment Configuration

The deployment uses the following persistent volumes:
- `bot-db-data`: Stores the SQLite database
- `bot-charts-data`: Stores generated charts and visualizations

Environment variables for the bot are stored in the GitHub repository secrets and deployed via the `.env` file.

## Rollback Procedure

If you need to rollback to a previous version:

1. Identify the Docker image tag for the previous working version
2. Manually trigger the deployment workflow
3. During the workflow run, specify the older image tag in the input field
4. The bot will be redeployed with the specified older version

## Monitoring

After deployment, monitor the bot's status:

1. Check the GitHub Actions workflow logs for successful completion
2. Verify the bot is responding to commands in Telegram
3. Monitor the server resources and logs if needed

## Troubleshooting

If deployment fails:

1. Check the GitHub Actions workflow logs for error details
2. Verify that all required secrets are properly configured
3. Ensure the target server is accessible and has sufficient resources
4. Contact the DevOps team if infrastructure issues occur