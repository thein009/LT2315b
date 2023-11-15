gcloud builds submit --tag gcr.io/geolab-sdn-bhd-lt2312/geolab-lt2315  --project=geolab-sdn-bhd-lt2312

gcloud run deploy --image gcr.io/geolab-sdn-bhd-lt2312/geolab-lt2315 --platform managed  --project=geolab-sdn-bhd-lt2312 --allow-unauthenticated