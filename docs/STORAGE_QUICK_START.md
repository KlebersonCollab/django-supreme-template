# Cloud Storage Quick Start

Quick reference for configuring cloud storage backends.

## AWS S3

```bash
STORAGE_BACKEND=s3
AWS_STORAGE_BUCKET_NAME=my-bucket
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_S3_REGION_NAME=us-east-1
```

## DigitalOcean Spaces

```bash
STORAGE_BACKEND=s3
AWS_STORAGE_BUCKET_NAME=my-space
AWS_ACCESS_KEY_ID=your-spaces-key
AWS_SECRET_ACCESS_KEY=your-spaces-secret
AWS_S3_REGION_NAME=nyc3
AWS_S3_ENDPOINT_URL=https://nyc3.digitaloceanspaces.com
```

## Google Cloud Storage

```bash
STORAGE_BACKEND=gcs
GS_BUCKET_NAME=my-bucket
GS_PROJECT_ID=my-project
GS_CREDENTIALS=/path/to/credentials.json
```

## Azure Blob Storage

```bash
STORAGE_BACKEND=azure
AZURE_ACCOUNT_NAME=myaccount
AZURE_ACCOUNT_KEY=your-key
AZURE_CONTAINER=my-container
```

## Local Storage (Default)

```bash
STORAGE_BACKEND=local
# or simply don't set STORAGE_BACKEND
```

For detailed configuration, see [STORAGE_BACKENDS.md](./STORAGE_BACKENDS.md).

