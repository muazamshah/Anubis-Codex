# ANUBIS CODEX - Deployment Guide

## Important: This Application Requires TWO Components

The ANUBIS CODEX application consists of:

1. **Backend (Python/FastAPI)** - Processes repositories, generates embeddings, manages AI chat
2. **Frontend (React/Vite)** - User interface for interacting with the application

**Both components must be running for the application to work.**

---

## Why GitHub Pages Alone Won't Work

GitHub Pages is a **static hosting service** that can only serve:
- HTML files
- CSS files  
- JavaScript files

It **CANNOT** run:
- Python code
- FastAPI server
- Backend APIs
- Database operations (ChromaDB)
- AI model inference

Your application needs the backend server to:
- Download and analyze GitHub repositories
- Parse code and generate embeddings
- Store data in ChromaDB vector database
- Call OpenRouter API for AI chat responses

---

## Deployment Options

### Option 1: Local Development (Recommended for Testing)

**Requirements:**
- Python 3.8+ installed
- Node.js 18+ installed
- Git installed

**Setup:**

Terminal 1 - Start Backend:
```bash
cd backend
uvicorn main:app --reload
```

Terminal 2 - Start Frontend:
```bash
cd frontend
npm run dev
```

Access at: http://localhost:5173

---

### Option 2: Deploy Backend to Cloud + Frontend to GitHub Pages

This is the closest to "GitHub Pages" deployment.

#### Step 1: Deploy Backend

Choose one of these free/cheap Python hosting services:

**A. Render.com (Recommended - Free Tier)**
1. Sign up at https://render.com
2. Create new "Web Service"
3. Connect your GitHub repository
4. Configure:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables:
   - `OPENROUTER_API_KEY` = your key
   - `GITHUB_TOKEN` = your token (optional)
6. Deploy

**B. Railway.app (Free Tier)**
1. Sign up at https://railway.app
2. Create new project from GitHub repo
3. Select `backend` folder
4. Add environment variables
5. Deploy

**C. Fly.io (Free Tier)**
1. Install Fly CLI
2. Run `fly launch` in backend directory
3. Follow prompts
4. Deploy with `fly deploy`

#### Step 2: Update Frontend Configuration

After deploying backend, update `frontend/vite.config.js`:

```javascript
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'https://your-backend-url.render.com', // Replace with your backend URL
        changeOrigin: true,
      },
    },
  },
});
```

#### Step 3: Deploy Frontend to GitHub Pages

1. Update `frontend/vite.config.js` for production:

```javascript
export default defineConfig({
  plugins: [react()],
  base: '/your-repo-name/', // Replace with your repo name
  build: {
    outDir: 'dist',
  },
});
```

2. Build the frontend:
```bash
cd frontend
npm run build
```

3. Deploy to GitHub Pages:
   - Use GitHub Actions (recommended)
   - Or manually push `dist` folder to `gh-pages` branch
   - Or use Netlify/Vercel (easier)

**Using Netlify (Easiest):**
1. Sign up at https://netlify.com
2. Drag and drop the `frontend/dist` folder
3. Or connect GitHub repo and configure build settings

---

### Option 3: Deploy Both to Same Service (Recommended for Production)

Deploy both frontend and backend together to one service.

#### A. Render.com (Full Stack)

1. **Deploy Backend:**
   - Follow Option 2A above
   - Note your backend URL (e.g., `https://anubis-codex-backend.onrender.com`)

2. **Deploy Frontend as Static Site:**
   - Create new "Static Site" on Render
   - Connect GitHub repo
   - Root Directory: `frontend`
   - Build Command: `npm install && npm run build`
   - Publish Directory: `dist`
   - Add environment variable:
     - `VITE_API_BASE` = `https://anubis-codex-backend.onrender.com`

3. **Update vite.config.js for production:**

```javascript
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
  },
});
```

4. **Update App.jsx to use environment variable:**

```javascript
// At the top of App.jsx
const API_BASE = import.meta.env.VITE_API_BASE || '';

// Rest of the code...
```

#### B. Railway.app (Full Stack)

1. Create new project
2. Add backend service (Python)
3. Add frontend service (Node.js)
4. Configure environment variables
5. Deploy both

#### C. VPS/DigitalOcean (Full Control)

1. Rent a VPS (starts at $4/month)
2. Install Python, Node.js, Nginx
3. Set up systemd services for backend
4. Build and serve frontend with Nginx
5. Configure domain name and SSL

---

## Environment Variables for Production

### Backend (.env on server)

```env
# REQUIRED
OPENROUTER_API_KEY=sk-or-v1-xxxxx

# OPTIONAL
GITHUB_TOKEN=ghp_xxxxx

# CONFIGURATION
LLM_PROVIDER=openrouter
LLM_MODEL=openrouter/free
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
VECTOR_DB_PATH=cache/vector_db
CACHE_DIR=/tmp/anubis-codex-cache
```

### Frontend (Environment Variables)

For Vite, create `frontend/.env.production`:

```env
VITE_API_BASE=https://your-backend-url.com
```

---

## Quick Start for Local Development

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/Anubis-Codex.git
cd Anubis-Codex
```

2. **Set up backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# OR source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
uvicorn main:app --reload
```

3. **Set up frontend (in new terminal):**
```bash
cd frontend
npm install
npm run dev
```

4. **Configure API key:**
```bash
# Edit backend/.env and add your OpenRouter API key
OPENROUTER_API_KEY=your_key_here
```

5. **Access application:**
```
http://localhost:5173
```

---

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.8+)
- Install dependencies: `pip install -r requirements.txt`
- Check if port 8000 is available

### Frontend won't start
- Check Node.js version: `node --version` (need 18+)
- Install dependencies: `npm install`
- Check if port 5173 is available

### "Analysis failed" error
- Backend is not running - start it with `uvicorn main:app --reload`
- Check backend logs for errors
- Verify API key is configured in `backend/.env`

### "Connection refused" error
- Backend server is not running
- Start backend first, then frontend
- Check firewall settings

### CORS errors
- Backend CORS is configured to allow all origins (`"*"`)
- If issues persist, check `backend/main.py` CORS settings

---

## Summary

**For Testing/Development:**
- Run both servers locally
- Use http://localhost:5173

**For Production:**
- Deploy backend to Render/Railway/Fly.io
- Deploy frontend to Netlify/Vercel/GitHub Pages
- Update frontend to point to deployed backend URL
- Configure environment variables on hosting service

**GitHub Pages Only:**
- ❌ Will NOT work - backend cannot run on GitHub Pages
- ✅ Can host frontend only, but needs separate backend deployment

---

## Cost Estimate

**Free Tier (for testing):**
- Backend: Render.com (free) or Railway (free trial)
- Frontend: Netlify (free) or Vercel (free)
- **Total: $0/month**

**Production (for real usage):**
- Backend: Render.com ($7/month) or Railway ($5/month)
- Frontend: Netlify Pro ($19/month) or Vercel Pro ($20/month)
- **Total: $12-26/month**

**VPS (most cost-effective for production):**
- DigitalOcean Droplet: $4/month
- Includes both frontend and backend
- **Total: $4/month**

---

## Support

For deployment issues:
1. Check the hosting service's documentation
2. Review application logs
3. Verify environment variables are set correctly
4. Test backend API endpoints directly
5. Check network/firewall settings