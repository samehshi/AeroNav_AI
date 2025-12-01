# Google Cloud Run Deployment Script

This script helps you deploy your NANSC Intelligent Operations Console to Google Cloud Run for production use.

## Prerequisites

- Google Cloud account with billing enabled
- Google Cloud SDK installed (`gcloud`)
- Google API key stored in Secret Manager

## Quick Start

```bash
# Make the script executable
chmod +x scripts/deploy_cloud_run.sh

# Run the deployment
./scripts/deploy_cloud_run.sh --project your-project-id --service-name nansc-console
```

## Usage

```bash
./scripts/deploy_cloud_run.sh [OPTIONS]
```

### Options

- `--project PROJECT_ID`: Your Google Cloud project ID
- `--service-name NAME`: Name of the Cloud Run service (default: nansc-console)
- `--region REGION`: Region for Cloud Run (default: us-central1)
- `--api-key KEY`: Your Google API key

## What This Script Does

1. **Setup**: Validates prerequisites and sets up the project
2. **Create Secret**: Stores your Google API key in Secret Manager
3. **Build**: Creates Docker image using Cloud Build
4. **Deploy**: Deploys to Cloud Run with proper permissions
5. **Configure**: Sets up IAM permissions for public access

## Cost Estimate

- **Compute**: $0.000024 per vCPU-second
- **Memory**: $0.0000025 per GB-second
- **Requests**: $0.40 per million requests
- **Network**: $0.12 per GB (egress)

**Estimated Monthly Cost:**
- Low usage: ~$5-10/month
- Medium usage: ~$20-50/month
- High usage: ~$100+/month

## Files Created

- `app.py`: Flask application
- `requirements.txt`: Python dependencies
- `Dockerfile`: Container configuration
- `cloudbuild.yaml`: Cloud Build configuration
- `service-account.json`: Service account key (if needed)

## Next Steps

After deployment:
1. Visit the Cloud Run console
2. Note your service URL
3. Configure custom domain (optional)
4. Set up monitoring and alerts

For more information, see the [Google Cloud Run Documentation](https://cloud.google.com/run/docs).