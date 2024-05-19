
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, Float, Boolean, DateTime, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import uvicorn
import datetime

# Initialize FastAPI app
app = FastAPI()

# Database URL
DATABASE_URL = "mysql+mysqlconnector://madesh:AVNS_M29-t16mlKN_KEyzBve@mysql-22499526-ofcea9fc1.database.cloud.ovh.us:17528/monitoring"

# Slack webhook URL
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

# Initialize SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define model for ping data
class PingData(Base):
    __tablename__ = 'ping_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    Microservice = Column(String(255))
    Product_Name = Column(String(255))
    response_time = Column(Float)
    status_code = Column(Integer)
    error = Column(Boolean)
    time_stamp = Column(DateTime)
    method = Column(String(50))
    api_endpoint = Column(String(255))

# Create the table if it does not exist
Base.metadata.create_all(bind=engine)

# Microservices list
microservices = [
    {"Microservice": "Admin Panel Frontend", "Product_Name": "Admin Panel Frontend", "type": "GET", "url": "https://admin.openinapp.com", "api_endpoint": "/"},
    {"Microservice": "Admin Panel Backend", "Product_Name": "Admin Panel Backend", "type": "GET", "url": "https://adminapinode.openinapp.com", "api_endpoint": "/"},
    # Add other microservices here...
]

# Function to ping microservices and store data
def ping_microservices():
    for service in microservices:
        try:
            start_time = datetime.datetime.now()
            if service["type"] == "GET":
                response = requests.get(service["url"])
            elif service["type"] == "POST":
                response = requests.post(service["url"], json={"key": "value"})
            end_time = datetime.datetime.now()
            response_time = (end_time - start_time).total_seconds()
            status_code = response.status_code
            error = False if 200 <= status_code < 400 else True

            # Store ping data in the database
            db = SessionLocal()
            try:
                ping_data = PingData(
                    Microservice=service["Microservice"],
                    Product_Name=service["Product_Name"],
                    response_time=response_time,
                    status_code=status_code,
                    error=error,
                    time_stamp=datetime.datetime.now(),
                    method=service["type"],
                    api_endpoint=service["api_endpoint"]
                )
                db.add(ping_data)
                db.commit()
            except Exception as e:
                db.rollback()
                raise HTTPException(status_code=500, detail=str(e))
            finally:
                db.close()
        except Exception as e:
            print(f"Error pinging {service['Microservice']}: {str(e)}")

# Function to calculate daily report
def generate_daily_report():
    db = SessionLocal()
    today = datetime.datetime.now().date()
    ping_data = db.query(PingData).filter(PingData.time_stamp >= today).all()
    db.close()

    report = ""
    for data in ping_data:
        avg_response_time = (data.response_time * 1000)  # Response time in milliseconds
        uptime = 100.0 if not data.error else 0.0
        error_rate = 0.0 if not data.error else 100.0
        report += f"Daily Report for {data.Microservice} ({today}):\n"
        report += f"Avg Response Time: {avg_response_time:.0f} milliseconds\n"  # Round to nearest integer
        report += f"Uptime: {uptime:.2f}%\n"
        report += f"Error Rate: {error_rate:.2f}%\n\n"
    return report

# Function to send daily report to Slack webhook URL
def send_daily_report():
    if not SLACK_WEBHOOK_URL:
        print("SLACK_WEBHOOK_URL not found in environment variables")
        return

    report = generate_daily_report()

    # Send report to Slack webhook
    payload = {"text": report}
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)

    if response.status_code == 200:
        print("Daily report sent successfully")
    else:
        print(f"Failed to send daily report. Status code: {response.status_code}")

# Schedule ping and send report functions to run every 60 seconds and 24 hours respectively
scheduler = BackgroundScheduler()
scheduler.add_job(ping_microservices, 'interval', seconds=60)
scheduler.add_job(send_daily_report, 'interval', hours=24)
scheduler.start()

# Run the FastAPI app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
