# EcoVision AI

Smart Waste Segregation and Monitoring System with:
- IoT sensor ingestion (Arduino HC-SR04 or simulator)
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

## Useful Commands
```powershell
# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Backend API quick check
curl http://localhost:8000/api/health
```
