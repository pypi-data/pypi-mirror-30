Qth Darksky
===========

Add weather forecasts powered by [Darksky](https://darksky.net/poweredby/) to
Qth.

The `qth_darksky` command takes four arguments: a Qth path to add the weather
forecast to, a Darksky API key, a longitude and a latitude. For example:

    $ qth_darksky --prefix=weather/stockport/ XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX 53.3933 -2.1266

This will create the following properties which summarise parts of the Darksky
forecast that I happen to be interested in...

* `weather/stockport/last-update`: Last update time (hh:mm:ss)
* `weather/stockport/last-update/unix`: Last update time (unix time)
* `weather/stockport/precipitation`: An array giving precipitation
  probabilities (0.0 - 1.0), one per hour, with the first being for the current
  hour.
* `weather/stockport/temperature`: An array giving temperature forecasts, one
  per hour, with the first being for the current hour.
* `weather/stockport/subjective-temperature`: An array giving feels-like
  temperature forecasts, one per hour, with the first being for the current
  hour.
* `weather/stockport/cloud-cover`: An array giving cloud cover
  (0.0 - 1.0) forecasts, one per hour, with the first being for the current
  hour.
* `weather/stockport/sunrise`: Today's sunrise time (hh:mm:ss)
* `weather/stockport/sunrise/unix`: Today's sunrise time (unix time)
* `weather/stockport/sunset`: Today's sunset time (hh:mm:ss)
* `weather/stockport/sunset/unix`: Today's sunset time (unix time)
