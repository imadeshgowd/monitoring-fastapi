
# Monitoring Microservices with FastAPI

This repository provides a FastAPI application to monitor various microservices. It pings the microservices at regular intervals, stores the response data in a MySQL database, and generates daily reports which are sent to a Slack channel.

## Features

- Pings a list of predefined microservices.
- Stores response times, status codes, and error flags in a MySQL database.
- Generates daily reports of the microservices' performance.
- Sends daily reports to a specified Slack channel.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- MySQL server
- Slack workspace

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/monitoring-fastapi.git
cd monitoring-fastapi
```

2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

3. Update the `DATABASE_URL` and `SLACK_WEBHOOK_URL` in the script with your MySQL database connection string and Slack webhook URL respectively.

### Running the Application

Start the FastAPI application:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The application will start pinging the microservices every 60 seconds and send a daily report to the specified Slack channel.

### Adding Microservices

To add more microservices to be monitored, update the `microservices` list in the script with the necessary details:

```python
microservices = [
    {"Microservice": "New Microservice", "Product_Name": "New Product", "type": "GET", "url": "https://newservice.example.com", "api_endpoint": "/"},
    # Add other microservices here...
]
```

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

For more information and to contribute, please visit [GitHub Repository](https://github.com/imadeshgowd/monitoring-fastapi).

---


