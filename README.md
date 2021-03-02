# Data-ingest Metrics

## Purpose

This project is about retrieving GCP services's time-series data (functions, Pub/Sub topics, etc...) and load it into
Big Query. The purpose is to explore data and provide dashboards which can be very useful for the data engineer or
people responsible of the RUN.

## Deployment

To deploy this function on your project, run the following command:

```bash
gcloud functions deploy \
 --trigger-http \
 --region="europe-west1" \
 --runtime="python37" \
 --allow-unauthenticated \
 "metrics_to_bigquery"
```

⚠️This function is meant to be used in combination with a Google Cloud Scheduler. Please create one with a one-minute
frequency (`* * * * *`) pointing to the URL of the metrics_to_bigquery function. You can choose the frequency you want
depending on your project purpose

## How

The function directly updates destination table set on *conf.yaml* file by populating it with needed metric time series
data that matches the choosen filter. A bunch of filters are set in *conf.yaml*. Feel free to add any filter you need.

For example of use, if you want to use datastudio, this table (or a big query view created from this table) will
represent the datasource of the datastudio dashboard.

```