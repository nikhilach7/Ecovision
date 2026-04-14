# EcoVision AI

Smart Waste Segregation and Monitoring System with:
- IoT sensor ingestion (Arduino HC-SR04 or simulator)
- ThingSpeak IoT dashboard support for field1-field4 charts
- AI waste image classification (plastic, metal, organic)
- FastAPI backend + MongoDB
- React dashboard with analytics
- JWT authentication + NLP query box

## Tech Stack
- Frontend: React + Vite + Tailwind + Recharts
- Backend: FastAPI (Python)
- Database: MongoDB (local, Docker, or Atlas)
- ML: TensorFlow/Keras

## Project Structure
- backend: API, ML service, scripts
- frontend: dashboard UI
- docker-compose.yml: full container setup

## Local Setup (Without Docker)

### 1. Start MongoDB
Use any one option:
- Local MongoDB service running on mongodb://localhost:27017
- MongoDB Atlas URI in backend/.env

### 1B. Optional: Configure ThingSpeak for IoT charts
If you want the IoT charts like in your screenshot, enable ThingSpeak in `backend/.env`:
```env
THINGSPEAK_ENABLED=true
THINGSPEAK_API_KEY=your_thingspeak_write_api_key
```

Field mapping used by the project:
- field1 = fill level
- field2 = waste level
- field3 = distance
- field4 = bin status

The simulator and serial bridge will send the same sensor readings to:
- your FastAPI backend
- ThingSpeak

### 2. Backend Setup
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Edit backend/.env and set at least:
```env
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=ecovision
JWT_SECRET=replace-with-a-strong-secret
STORAGE_BACKEND=local
```

If using Atlas:
```env
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster-url>/
STORAGE_BACKEND=gridfs
```

### 3. Optional: Generate Dataset + Train Model
```powershell
python scripts/generate_sample_dataset.py
python scripts/train_model.py
```

### Preferred: Use a TrashNet-style dataset
If you want a more realistic training dataset, download TrashNet directly from Hugging Face and convert it into the raw folder used by this project.

Direct download command:
```powershell
python scripts/download_trashnet_hf.py
```

This script uses Hugging Face streaming and saves a balanced subset per class, so it does not need to download the full 3.4 GB dataset.

This creates the raw folder here:
```text
backend/data/trashnet_raw/
```

Then prepare the compact 3-class dataset used by this project:
```powershell
python scripts/prepare_trashnet_dataset.py
python scripts/train_model.py
```

The project maps the raw dataset into these final classes:
- plastic -> plastic
- metal -> metal
- paper/cardboard/trash -> organic

If you want to use the exact Hugging Face API snippet, it is:
```python
from datasets import load_dataset

ds = load_dataset("garythung/trashnet")
```

If you do not have a real dataset yet, the synthetic generator still works as a fallback.

### No-Dataset Option (Fastest)
You can run the app without downloading any dataset.

If `backend/model/waste_classifier.keras` is missing, the backend automatically uses an ImageNet-pretrained MobileNetV2 inference fallback and maps predictions to:
- plastic
- metal
- organic

So you can continue development/demo immediately, then train a project-specific model later.

### 4. Run Backend
```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Run Sensor Simulator (optional)
Open a new terminal:
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python scripts/sensor_simulator.py
```

If ThingSpeak is enabled, the simulator also updates the ThingSpeak channel fields.

### 6. Frontend Setup
Open another terminal:
```powershell
cd frontend
npm install
npm run dev
```

### 7. Open App
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api
- Health: http://localhost:8000/api/health

## Docker Setup (Full Stack)

### 1. Start All Services
From project root:
```powershell
docker compose up --build -d
```

### 2. Check Containers
```powershell
docker compose ps
```

### 3. Optional: Train Model Inside Backend Container
```powershell
docker compose exec backend python scripts/generate_sample_dataset.py
docker compose exec backend python scripts/train_model.py
```

### 4. Optional: Run Sensor Simulator in Container
```powershell
docker compose exec backend python scripts/sensor_simulator.py
```

If ThingSpeak is enabled in the container env, field1-field4 are updated there too.

### 5. Open App
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api
- Health: http://localhost:8000/api/health

### 6. Stop Services
```powershell
docker compose down
```

### 7. Clean Reset (remove volumes)
```powershell
docker compose down -v
```

## Docker with MongoDB Atlas (Cloud)
If you want Dockerized app + Atlas database:
1. Update backend environment in docker-compose.yml
2. Set:
- MONGODB_URI=mongodb+srv://<username>:<password>@<cluster-url>/
- STORAGE_BACKEND=gridfs
3. Start app services:
```powershell
docker compose up --build -d backend frontend
```

## Demo Flow
1. Register account and login.
2. Upload waste images.
3. Check dashboard charts and cloud cards.
4. Ask NLP queries (example: How much plastic waste today?).
5. Watch bin-full alerts when fill level exceeds 90%.
6. If ThingSpeak is enabled, confirm live field1-field4 charts in ThingSpeak.

## Useful Commands
```powershell
# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Backend API quick check
curl http://localhost:8000/api/health
```
