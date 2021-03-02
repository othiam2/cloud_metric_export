import logging
from typing import Any
from google.cloud import monitoring_v3, bigquery

import time

from google.cloud.monitoring_v3 import TimeInterval, ListTimeSeriesRequest, TimeSeries
from google.cloud.monitoring_v3.types import Aggregation

from config import configs

client = monitoring_v3.MetricServiceClient()
project_name = f"projects/{configs.get('project')}"

# Time interval calculation
now = time.time()
seconds = int(now)
nanos = int((now - seconds) * 10 ** 9)
interval = TimeInterval(
    {
        "end_time": {"seconds": seconds, "nanos": nanos},
        "start_time": {"seconds": (seconds - 3600), "nanos": nanos},
        # 60 minutes. We are retrieving metrics with the past hour
    }
)


def metrics_to_bigquery(metric_type: Any):
    """
        Configure all the metric parameters and push time series
        data into big query

        :param: metric_type: complete metric type name.
        """
    # Set aggregation properties as we need to aggregate points by a defined period of time. eg. by minute
    add_par = Aggregation(
        {
            "alignment_period": {"seconds": 60},  # By minute
            "per_series_aligner": Aggregation.Aligner.ALIGN_PERCENTILE_50 \
                if metric_type == 'metric.type="cloudfunctions.googleapis.com/function/user_memory_bytes"' else \
                Aggregation.Aligner.ALIGN_SUM,
            # As this metric type is a Distribution one, we have to use the appropriate Aligner property
            "group_by_fields": [configs.get_groubbyfield(metric_type)] if configs.get_groubbyfield(
                metric_type) is not None else None
            # groupBy field defined in conf.yaml. The group by field may depend on the metric you need to retrieve and \
            # is up to the data engineer
        }
    )

    # Get the time series that match the filter (or metric type)
    metrics = client.list_time_series(
        request={
            "name": project_name,
            "filter": metric_type,
            "interval": interval,
            "view": ListTimeSeriesRequest.TimeSeriesView.FULL,
            "aggregation": add_par,
        }
    )

    # Big Query client to put time series data into specified big query table
    bq_client = bigquery.Client()
    metric_dicts = [TimeSeries.to_dict(metric) for metric in metrics]
    if not metric_dicts:
        logging.info(
            f"No rows to be inserted for metric {metric_type} in the time interval [{interval.start_time};{interval.end_time}]")
    else:
        bq_client.insert_rows_json(table=f"{configs.get('dataset')}.{configs.get('table')}", json_rows=metric_dicts)
        logging.info(
            f"Inserted metric {metric_type} into big query table {configs.get('dataset')}.{configs.get('table')}")


# Insert into big query for every filter as parameter
for flt in configs.get_filters():
    metrics_to_bigquery(flt)
