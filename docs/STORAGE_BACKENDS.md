# Cloud Storage Backends Configuration

This template supports multiple cloud storage backends for static and media files:

- **AWS S3** (Amazon Web Services)
- **Google Cloud Storage** (GCS)
- **Azure Blob Storage** (Microsoft)
- **DigitalOcean Spaces** (S3-compatible)
- **Scaleway Object Storage** (S3-compatible)
- **MinIO** (S3-compatible)
- **Local Storage** (default, for development)

## Quick Configuration

Set the `STORAGE_BACKEND` environment variable to one of:
- `local` - Local file system (default)
- `s3` - AWS S3 or S3-compatible services
- `gcs` - Google Cloud Storage
- `azure` - Azure Blob Storage

## AWS S3 Configuration

### Basic Setup

```bash
STORAGE_BACKEND=s3
AWS_STORAGE_BUCKET_NAME=my-bucket-name
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_S3_REGION_NAME=us-east-1
```

### Advanced Options

```bash
# Custom endpoint (for S3-compatible services like DigitalOcean Spaces)
AWS_S3_ENDPOINT_URL=https://nyc3.digitaloceanspaces.com

# Custom domain (CDN)
AWS_S3_CUSTOM_DOMAIN=cdn.example.com

# Location prefix in bucket
AWS_S3_LOCATION=media

# Separate bucket for static files
AWS_STATIC_BUCKET_NAME=my-static-bucket

# ACL settings
AWS_DEFAULT_ACL=public-read

# URL expiration (seconds)
AWS_QUERYSTRING_EXPIRE=3600
```

### DigitalOcean Spaces Example

```bash
STORAGE_BACKEND=s3
AWS_STORAGE_BUCKET_NAME=my-space
AWS_ACCESS_KEY_ID=your-spaces-key
AWS_SECRET_ACCESS_KEY=your-spaces-secret
AWS_S3_REGION_NAME=nyc3
AWS_S3_ENDPOINT_URL=https://nyc3.digitaloceanspaces.com
```

### Scaleway Object Storage Example

```bash
STORAGE_BACKEND=s3
AWS_STORAGE_BUCKET_NAME=my-bucket
AWS_ACCESS_KEY_ID=SCWXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_S3_REGION_NAME=nl-ams
AWS_S3_ENDPOINT_URL=https://s3.nl-ams.scw.cloud
```

### MinIO Example

```bash
STORAGE_BACKEND=s3
AWS_STORAGE_BUCKET_NAME=my-bucket
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
AWS_S3_REGION_NAME=us-east-1
AWS_S3_ENDPOINT_URL=http://localhost:9000
```

## Google Cloud Storage Configuration

### Basic Setup

```bash
STORAGE_BACKEND=gcs
GS_BUCKET_NAME=my-bucket-name
GS_PROJECT_ID=my-project-id
GS_CREDENTIALS=/path/to/credentials.json
```

### Using Environment Variable for Credentials

If using `GOOGLE_APPLICATION_CREDENTIALS` environment variable:

```bash
STORAGE_BACKEND=gcs
GS_BUCKET_NAME=my-bucket-name
GS_PROJECT_ID=my-project-id
# GS_CREDENTIALS not needed if GOOGLE_APPLICATION_CREDENTIALS is set
```

### Advanced Options

```bash
# Location prefix in bucket
GS_LOCATION=media

# Separate bucket for static files
GS_STATIC_BUCKET_NAME=my-static-bucket

# ACL settings
GS_DEFAULT_ACL=publicRead

# URL expiration (seconds, max 7 days)
GS_EXPIRATION=86400

# Query string authentication
GS_QUERYSTRING_AUTH=True
```

### Getting GCS Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to "IAM & Admin" > "Service Accounts"
3. Create a new service account or use existing
4. Create a JSON key and download it
5. Set `GS_CREDENTIALS` to the path of the JSON file

## Azure Blob Storage Configuration

### Basic Setup

```bash
STORAGE_BACKEND=azure
AZURE_ACCOUNT_NAME=myaccount
AZURE_ACCOUNT_KEY=your-account-key
AZURE_CONTAINER=my-container
```

### Using Connection String

```bash
STORAGE_BACKEND=azure
AZURE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=myaccount;AccountKey=...
AZURE_CONTAINER=my-container
```

### Advanced Options

```bash
# Location prefix in container
AZURE_LOCATION=media

# Separate container for static files
AZURE_STATIC_CONTAINER=static-container

# Custom domain (CDN)
AZURE_CUSTOM_DOMAIN=cdn.example.com

# URL expiration (seconds)
AZURE_URL_EXPIRATION_SECS=3600

# Overwrite files
AZURE_OVERWRITE_FILES=True
```

### Getting Azure Credentials

1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to your Storage Account
3. Go to "Access keys" section
4. Copy the account name and key

## Local Storage (Default)

For development, local storage is used by default:

```bash
STORAGE_BACKEND=local
# or simply don't set STORAGE_BACKEND
```

Files are stored in:
- Static files: `STATIC_ROOT` (default: `staticfiles/`)
- Media files: `MEDIA_ROOT` (default: `media/`)

## Environment Variables Reference

### Common Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `STORAGE_BACKEND` | Storage backend: `local`, `s3`, `gcs`, `azure` | `local` |

### AWS S3 Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `AWS_STORAGE_BUCKET_NAME` | S3 bucket name | Yes |
| `AWS_ACCESS_KEY_ID` | AWS access key | Yes |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | Yes |
| `AWS_S3_REGION_NAME` | AWS region | No (default: us-east-1) |
| `AWS_S3_ENDPOINT_URL` | Custom endpoint (for S3-compatible) | No |
| `AWS_S3_CUSTOM_DOMAIN` | Custom domain/CDN | No |
| `AWS_S3_LOCATION` | Path prefix in bucket | No |
| `AWS_STATIC_BUCKET_NAME` | Separate bucket for static files | No |
| `AWS_S3_STATIC_LOCATION` | Static files location | No (default: static) |
| `AWS_DEFAULT_ACL` | Default ACL (e.g., public-read) | No |
| `AWS_QUERYSTRING_AUTH` | Use query string auth | No (default: True) |
| `AWS_QUERYSTRING_EXPIRE` | URL expiration (seconds) | No (default: 3600) |
| `AWS_S3_FILE_OVERWRITE` | Overwrite existing files | No (default: True) |

### Google Cloud Storage Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GS_BUCKET_NAME` | GCS bucket name | Yes |
| `GS_PROJECT_ID` | GCP project ID | Yes |
| `GS_CREDENTIALS` | Path to credentials JSON | No* |
| `GS_LOCATION` | Path prefix in bucket | No |
| `GS_STATIC_BUCKET_NAME` | Separate bucket for static files | No |
| `GS_STATIC_LOCATION` | Static files location | No (default: static) |
| `GS_DEFAULT_ACL` | Default ACL (e.g., publicRead) | No |
| `GS_QUERYSTRING_AUTH` | Use query string auth | No (default: True) |
| `GS_EXPIRATION` | URL expiration (seconds) | No (default: 86400) |
| `GS_FILE_OVERWRITE` | Overwrite existing files | No (default: True) |

*Required if `GOOGLE_APPLICATION_CREDENTIALS` is not set

### Azure Blob Storage Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `AZURE_ACCOUNT_NAME` | Azure storage account name | Yes* |
| `AZURE_ACCOUNT_KEY` | Azure storage account key | Yes* |
| `AZURE_CONNECTION_STRING` | Full connection string | Yes* |
| `AZURE_CONTAINER` | Container name | Yes |
| `AZURE_LOCATION` | Path prefix in container | No |
| `AZURE_STATIC_CONTAINER` | Separate container for static files | No |
| `AZURE_STATIC_LOCATION` | Static files location | No (default: static) |
| `AZURE_CUSTOM_DOMAIN` | Custom domain/CDN | No |
| `AZURE_URL_EXPIRATION_SECS` | URL expiration (seconds) | No (default: 3600) |
| `AZURE_OVERWRITE_FILES` | Overwrite existing files | No (default: True) |

*Either `AZURE_ACCOUNT_NAME` + `AZURE_ACCOUNT_KEY` OR `AZURE_CONNECTION_STRING`

## Usage in Code

The storage backend is automatically configured. Use Django's file handling as usual:

```python
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

# Save a file
file = ContentFile(b"Hello, World!")
default_storage.save("test.txt", file)

# Read a file
file = default_storage.open("test.txt")
content = file.read()

# Get file URL
url = default_storage.url("test.txt")
```

## Collecting Static Files

When using cloud storage for static files, run:

```bash
python manage.py collectstatic --noinput
```

This will upload all static files to your configured storage backend.

## Migration from Local to Cloud

1. Set up your cloud storage account
2. Configure environment variables
3. Run `collectstatic` to upload static files
4. Existing media files need to be migrated manually (if any)

## Security Best Practices

1. **Never commit credentials** to version control
2. Use **IAM roles** when possible (AWS, GCP)
3. Use **service accounts** with minimal permissions
4. Enable **bucket versioning** for important files
5. Use **CDN** with custom domains for public files
6. Set appropriate **ACLs** based on file sensitivity
7. Use **signed URLs** for private files

## Troubleshooting

### S3: Access Denied

- Check IAM permissions
- Verify bucket policy
- Ensure credentials are correct

### GCS: Authentication Error

- Verify credentials JSON path
- Check service account permissions
- Ensure `GOOGLE_APPLICATION_CREDENTIALS` is set if not using `GS_CREDENTIALS`

### Azure: Connection Failed

- Verify account name and key
- Check container exists
- Ensure connection string format is correct

### Files Not Uploading

- Check bucket/container exists
- Verify write permissions
- Check network connectivity
- Review Django logs for errors

