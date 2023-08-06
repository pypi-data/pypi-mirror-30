import math
import os
import syslog
from datetime import datetime, date, timedelta

import pandas as pd
from fbprophet import Prophet


class Detector:
    def __init__(self, min_time_points: int = 10, ignore_empty_dataset: bool = True) -> None:
        self.ds_min_points = min_time_points
        self.ignore_empty_dataset = ignore_empty_dataset

        self.x_column_name = 'ds'
        self.y_column_name = 'y'

    def find_all_anomalies(self, dataset: pd.DataFrame) -> pd.DataFrame:
        """
        Forecast value based on history dataset and mark them as anomaly if it's outside of forecasted range
        Input should be a pandas DataFrame having "time" & "value" fields
        Output is a pandas DataFrame having all forecasts & anomalies
        :param dataset:
               pd.DataFrame([{"time": "2018-02-13", "value": 1069}, {"time": "2018-02-14", "value": 3000}, ...])
               data should be aggregated per day for example there should be only one entry (value) for each day
        :return:
                 each Series has "ds", "trend", "trend_lower", "trend_upper", "yhat_lower", "yhat_upper", "seasonal",
                 "seasonal_lower", "seasonal_upper", "seasonalities", "seasonalities_lower", "seasonalities_upper",
                 "weekly", "weekly_lower", "weekly_upper", "yhat", "std", "actual"
                 For more info check https://facebook.github.io/prophet/
        """

        dataset = self._validate_input(dataset)
        forecast = self._get_forecast(dataset)
        anomalies = pd.DataFrame()
        if not forecast.empty:
            forecast['actual'] = dataset[self.y_column_name]
            anomalies = pd.concat([
                forecast[forecast['actual'] > forecast['yhat_upper']],
                forecast[forecast['actual'] < forecast['yhat_lower']]
            ]).sort_values(self.x_column_name) if not forecast.empty else forecast
        return anomalies

    def forecast_today(self, dataset: pd.DataFrame) -> pd.DataFrame:
        """
        Forecast today based on history dataset and mark today as anomaly if it's outside of forecasted range
        Input should an array of json objects having `time` & `value` fields
        Output is an array of json objects having today's forecast & anomaly
        :param dataset:
               pd.DataFrame([{"time": "2018-02-13", "value": 1069}, {"time": "2018-02-14", "value": 3000}, ...])
               data should be aggregated per day for example there should be only one entry (value) for each day
        :return: pd.DataFrame of anomalies
                 each Series has "ds", "trend", "trend_lower", "trend_upper", "yhat_lower", "yhat_upper", "seasonal",
                 "seasonal_lower", "seasonal_upper", "seasonalities", "seasonalities_lower", "seasonalities_upper",
                 "weekly", "weekly_lower", "weekly_upper", "yhat", "std", "actual"
                 For more info check https://facebook.github.io/prophet/
        """

        dataset = self._validate_input(dataset)
        historical_data = dataset[dataset[self.x_column_name] != self._today()]
        todays_data = dataset[dataset[self.x_column_name] == self._today()]
        todays_forecast = self._get_forecast(historical_data, 'today')
        return self._compare(todays_data, todays_forecast)

    def _validate_input(self, dataset: pd.DataFrame) -> pd.DataFrame:
        x_column_name = 'time'
        y_column_name = 'value'
        if x_column_name not in dataset.columns or y_column_name not in dataset.columns:
            raise ValueError('dataset should have [{}] & [{}] columns'.format(x_column_name, y_column_name))

        dataset = dataset.rename(columns={x_column_name: self.x_column_name, y_column_name: self.y_column_name})

        dataset[self.x_column_name].apply(lambda t: t.strftime('%Y-%m-%d') if isinstance(t, date) else t)

        return dataset

    def _get_forecast(self, data: pd.DataFrame, type: str = 'all the time') -> pd.DataFrame:
        actual_time_points = len(data)
        actual_dataset_size = data[self.y_column_name].sum()
        if actual_time_points < self.ds_min_points or (
                self.ignore_empty_dataset and int(math.ceil(actual_dataset_size) is 0)
        ):
            msg = "Skipped as min x [time] points did'nt match: actual [{}] < expected [{}]".format(
                actual_time_points,
                self.ds_min_points
            )
            msg += " or y [values] sum is zero: actual [{}]".format(actual_dataset_size)
            syslog.syslog(syslog.LOG_ERR, msg)
            return pd.DataFrame()

        forecast = self._forecast(data)
        return forecast[forecast['ds'] == self._today()] if type == 'today' else forecast

    def _forecast(self, data: pd.DataFrame) -> pd.DataFrame:
        model = Prophet(daily_seasonality=False, growth='logistic')
        prophet_input = pd.DataFrame()
        prophet_input['ds'] = data[self.x_column_name]
        prophet_input['y'] = data[self.y_column_name]
        cap = 2 * max(data[self.y_column_name])
        prophet_input['cap'] = cap
        prophet_input['floor'] = 0
        with suppress_stdout_stderr():
            model.fit(prophet_input)
        last_day_of_data = datetime.strptime(data[self.x_column_name].tail(1).values[0], '%Y-%m-%d')
        number_of_days_from_data_last_day_till_today = (datetime.today() - last_day_of_data).days
        future = model.make_future_dataframe(periods=number_of_days_from_data_last_day_till_today)
        future['cap'] = cap
        future['floor'] = 0
        return model.predict(future)

    def _compare(self, actual: pd.DataFrame, forecast: pd.DataFrame) -> pd.DataFrame:
        anomaly = pd.DataFrame()
        if actual.empty or forecast.empty:
            syslog.syslog(syslog.LOG_ERR, 'actual data or forecast is empty')
            return pd.DataFrame()

        forecast_lower_bound = forecast['yhat_lower'].values[0]
        forecast_upper_bound = forecast['yhat_upper'].values[0]
        forecast_value = forecast['yhat'].values[0]
        actual_value = actual[self.y_column_name].values[0]

        # diff = min(abs(actual_value - forecast_upper_bound), abs(actual_value - forecast_lower_bound))
        diff = actual_value - forecast_value
        if actual_value and round(abs(diff)) > 0:
            anomaly = forecast
            forecast_range = forecast_upper_bound - forecast_lower_bound
            change = diff / forecast_range
            anomaly['change'] = change
            severity = math.ceil(abs(change / (forecast_range / 6)))
            anomaly['severity'] = severity if severity < 5 else 5
            anomaly['actual'] = actual_value

        return anomaly

    def _today(self, days_back=0):
        d = datetime.today() - timedelta(days_back)
        return d.strftime('%Y-%m-%d')


class suppress_stdout_stderr(object):
    """
    A context manager for doing a "deep suppression" of stdout and stderr
    """

    def __init__(self):
        # Open a pair of null files
        self.null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]
        # Save the actual stdout (1) and stderr (2) file descriptors.
        self.save_fds = (os.dup(1), os.dup(2))

    def __enter__(self):
        # Assign the null pointers to stdout and stderr.
        os.dup2(self.null_fds[0], 1)
        os.dup2(self.null_fds[1], 2)

    def __exit__(self, *_):
        # Re-assign the real stdout/stderr back to (1) and (2)
        os.dup2(self.save_fds[0], 1)
        os.dup2(self.save_fds[1], 2)
        # Close the null files
        os.close(self.null_fds[0])
        os.close(self.null_fds[1])
