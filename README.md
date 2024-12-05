# WHIB Bot

WHIB (Where Have I Been) Bot (can be accessed at [t.me/whibBY_bot]()) is a microservice-based application that allows users to track their travels around Belarus and generates maps of visited regions/districts. It includes the following components:

## Architecture
* **Flask Web App**: Provides a REST API for managing user data and map generation.
* **Redis**: Used for caching data to improve performance.
* **PostGIS Database**: Stores and processes geographic user data.
* **Telegram Bot**: Asynchronous bot for user interaction and API communication.
## Features
* **Travel Tracking**: Log and manage travel data through the Telegram bot — either find a place by its name or attach the location.
* **Map Generation**: Generate maps highlighting visited regions or districts.
* **High Performance**: Utilizes Redis caching and asynchronous processing for efficiency.

Example of the generated map:

[![Districts-visited-map.png](https://i.postimg.cc/mDqjC1C3/Districts-visited-map.png)](https://postimg.cc/hzLVqjCh)