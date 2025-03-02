# DreamCanvas Analysis Microservice
This guide provides instructions to set up and run the DreamCanvas Analysis Microservice locally.

## Setup and Run Locally

### Step 1: Clone the Repo
```bash
git clone https://github.com/Lianyic/DreamCanvas-Analysis.git
cd DreamCanvas-Analysis
```

### Step 2: Create an .env file:
```bash
SECRET_KEY=your secret key
OPENAI_API_KEY=your openAI key
AUTH_SERVICE_URL=http://dreamcanvas-auth.ukwest.azurecontainer.io:5000/
DATABASE_URL=mysql+pymysql://adminuser:LeilaLily?!@dreamanalysis.mysql.database.azure.com/dream_analysis_db
REDIS_HOST=dreamcanvas-redis.redis.cache.windows.net
REDIS_PORT=6380
REDIS_PASSWORD=your redis password
```

### Step 3: Create & Activate a Virtual Environment
```bash
python -m venv dreamvenv
dreamvenv\Scripts\activate
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Apply Database Migrations
Do not follow if you have changed the database configuration  
Before running the app, ensure the database is up to date:
```bash
flask db upgrade
```

### Step 6: Run the app
default running at http://127.0.0.1:5001/record
```bash 
python app/app.py 
```

## Access the Deployed Service
DreamCanvas Analysis Service is automatically deployed via GitHub Actions and is accessible at:  
http://dreamcanvas-analysis.ukwest.azurecontainer.io:5001/

### Check database
```
mysql -h dreamcanvas-user-db.mysql.database.azure.com -u adminuser -p --ssl-mode=REQUIRED
```
