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

### Step 5: Apply Database Migrations (Do not follow if you have changed the database configuration)
Before running the app, ensure the database is up to date:
```bash
flask db upgrade
```

### Step 6: Run the app
```bash 
python app/app.py 
or 
flask run
```

## Access the Deployed Service
DreamCanvas Analysis Service is automatically deployed via GitHub Actions and is accessible at: http://dreamcanvas-analysis.ukwest.azurecontainer.io:5001/

### Check database
```
mysql -h dreamcanvas-user-db.mysql.database.azure.com -u adminuser -p --ssl-mode=REQUIRED
```
