# This is the DreamCanvas analysis page Intructions
This guide will help you set up and run the DreamCanvas dream analysis Microservice locally.

## Step 1: Clone the Repo
```bash
git clone https://github.com/Lianyic/DreamCanvas-Analysis.git
cd DreamCanvas-Analysis
```

## Step 2: Create an .env file:
```bash
SECRET_KEY=your secret key
OPENAI_API_KEY=your openAI key
AUTH_SERVICE_URL=http://dreamcanvas-auth.ukwest.azurecontainer.io:5000/
DATABASE_URL=mysql+pymysql://adminuser:LeilaLily?!@dreamanalysis.mysql.database.azure.com/dream_analysis_db
REDIS_HOST=dreamcanvas-redis.redis.cache.windows.net
REDIS_PORT=6380
REDIS_PASSWORD=Your redis password
```

## Step 3: Create & Activate a Virtual Environment
```bash
python -m venv dreamvenv
dreamvenv\Scripts\activate  # Windows
source dreamvenv/bin/activate  # macOS/Linux
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

## Step 7: Push changes to github(auto deployment to ACI)
```bash 
git add .
git commit -m "Your commit message"
git push origin master
```

# Auto Deployed to Github, available at URL:
## ACI web access URL
http://dreamcanvas-analysis.ukwest.azurecontainer.io:5001/

## Check database
```
mysql -h dreamcanvas-user-db.mysql.database.azure.com -u adminuser -p --ssl-mode=REQUIRED
```

## Local Docker Run Step

## Build the docker image
```
docker build -t dreamcanvas-analysis-service .
```

## Run the container locally
```
docker run -p 5001:5001 --env-file .env dreamcanvas-analysis-service
```

