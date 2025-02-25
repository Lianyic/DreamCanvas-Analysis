# This is the DreamCanvas analysis page Intructions
This guide will help you set up and run the DreamCanvas dream analysis Microservice locally.

## Step 1: Clone the Repo
```bash
git clone https://github.com/Lianyic/DreamCanvas-Analysis.git
cd DreamCanvas-Analysis
```

## Step 2: Create an .env file:
```bash
```

## Step 3: Create & Activate a Virtual Environment
```bash
python -m venv dreamvenv
dreamvenv\Scripts\activate
```

## Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

## Step 5: Apply Database Migrations (Do not follow if you have changed the database configuration)
### Before running the app, ensure the database is up to date:
```bash
flask db upgrade
```

## Step 6: Run the app
```bash 
python app.py 
or 
flask run
```

# Auto Deployed to Github, available at URL:
## ACI web access URL
http://dreamcanvas-analysis.ukwest.azurecontainer.io:5001/

## Check database
```
mysql -h dreamcanvas-user-db.mysql.database.azure.com -u adminuser -p --ssl-mode=REQUIRED
```


