# Stripe Sync
This project integrates Stripe's customer catalog into a backend application built with FastAPI, utilizing Kafka for asynchronous message processing.

## Technologies Used
- **FastAPI**: Asynchronous web framework for building APIs with Python 3.7+.
- **Kafka**: Used for message queuing and processing asynchronous tasks.
- **SQLAlchemy**: SQL toolkit and ORM for database operations.
- **Stripe API**: For managing customer data.
- **Ngrok**: To expose local webhook endpoints to the internet.
- **Uvicorn**: ASGI server for running FastAPI.
- **Alembic**: Used for Database Migrations

## Requirements
- Python 3.7+
- PostgreSQL or any SQL database
- Kafka
- Ngrok account (for local development)

## Screenshots:

Openapi Docs:
![image](https://github.com/Addy-codes/stripe-sync/assets/72205091/3623b96c-73f6-4c92-bb37-c6c5cc4b7c4c)

Postgres:
![image](https://github.com/Addy-codes/stripe-sync/assets/72205091/734bc8bc-373a-4b62-a104-221ea1bb8ea2)

Stripe Dashboard:
![image](https://github.com/Addy-codes/stripe-sync/assets/72205091/20b090eb-dac8-4714-afec-b3ce33026d64)


## Project Setup

### 1. Clone the Repository
```bash
git clone https://yourrepositorylink.git
cd stripe-sync
```

### 2. Set Up a Virtual Environment
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

### 3. Install Requirements
```bash
pip install -r requirements.txt
```

### 4. Create and Configure `.env` File
Create a `.env` file in the root directory of your project and update it with your API keys and database credentials:
```plaintext
DB_HOST=localhost
DB_NAME=zenskar
DB_USER=your-username
DB_PASSWORD=your-password
STRIPE_API_KEY=pk_test_your-api-key
STRIPE_SECRET_KEY=whsec_your-secret-key
```
### 5. Database Setup
Navigate to the root directory of your project where the `alembic.ini` file is located and run the following command to apply migrations:
```bash
alembic upgrade head
```
### 6. Start Kafka
Run kafka using docker:
```bash
docker-compose up
```
### 7. Start Ngrok
To expose your local server to the internet for Stripe webhook testing:
```bash
ngrok http 8000
```
Copy the HTTPS URL provided by Ngrok to your Stripe webhook settings.

### 8. Running the Application
Run the FastAPI application using Uvicorn:
```bash
uvicorn main:app --reload
```

### 9. Setup Stripe Webhook
Go to your Stripe Dashboard and set the webhook to point to the URL provided by Ngrok followed by `/api/stripe-webhook`.

### 10. Run Workers
Start the workers that will handle Kafka messages:
```bash
python workers.py
```

## Usage
The API can be accessed via `http://localhost:8000` or through the Ngrok URL when running locally. Use endpoints such as `/api/customers` for managing customer data and `/api/stripe-webhook` to handle incoming Stripe events.
One can also view and interact with the API using 'http://localhost:8000/docs'

---

### Additional Planning for Salesforce Integration (Future Development)
Future plans include adding integration with Salesforce's customer catalog. This will follow a similar design pattern to the existing Stripe integration, involving separate Kafka topics and a modular approach for scalability and maintainability.

To effectively integrate Salesforce into our application, we'll start by developing a dedicated module specifically for interacting with Salesforce's API. We'll use the `simple-salesforce` Python library for this purpose because it simplifies the process of making REST API calls and managing authentication. This module will not only handle the sending and receiving of data but also ensure that any data received from Salesforce is properly formatted to match our internal system's requirements, such as matching IDs, names, and emails.

Based on the webhook-endpoint, we'll setup the `service_name` column in the `id_map` table.

To manage the data flow smoothly and maintain system integrity, we'll set up separate Kafka topics specifically for Salesforce integration. This approach will help us avoid any potential conflicts with other parts of our system and allow us to scale and troubleshoot the Salesforce integration independently.

Additionally, we'll implement a worker service that listens to the Salesforce Kafka topic. This worker will be responsible for processing incoming data from Salesforce according to our predefined business rules and then updating our database accordingly. This setup ensures that our application remains responsive and efficient, even as data flows in from Salesforce.

To capture updates from Salesforce as they happen, we plan to set up webhooks within Salesforce. These webhooks will push updates directly to an endpoint in our system, which will be specifically designed to accept and process these calls. This real-time data synchronization will help keep our application's data current and accurate, reflecting any changes in Salesforce immediately.

### Extending Customer Catalog to support other systems

Firstly we'll have to allow other "Event to send" from stripe or any service that we will be using and create multiple webhook endpoints because:
- As the number of event types grows, a single endpoint could become a bottleneck, handling an increasing amount of traffic and more complex routing logic.
- Scaling becomes more manageable as each webhook can be scaled independently based on the volume and characteristics of the events it handles.

For example:- To integrate the invoice catalog into our product, we'll develop a new module dedicated to fetching invoice data from our database and publishing it to a designated Kafka topic. This data will be formatted to align with the specifications of the external system we aim to integrate with. Additionally, we will implement a complementary module that pulls invoice data from the external system and publishes it onto a separate Kafka topic. This module will also include functionality to transform the data to conform to our product's internal data model. These steps ensure seamless data flow and integration consistency between our system and external services.
