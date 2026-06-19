# 🚀 DesiFinds Deployment & Hosting Guide (GitHub, Render, and Vercel)

Since DesiFinds consists of a **React Frontend** and a **Python Backend (FastAPI)**, we deploy them on platforms optimized for each service:
1. **Render** (Free Tier): Hosts the Python/Docker backend server.
2. **Vercel** (Free Tier): Hosts the static React frontend.

Follow this guide to get your application live.

---

## 🛠️ Step 1: Push Your Code to GitHub

First, you need to save the project on GitHub so Render and Vercel can pull the code directly.

1. Go to [github.com](https://github.com/) and create a new repository named `desi-finds`. Keep it public or private.
2. Open a terminal in the root project folder (`c:\Users\Bhagya B\Downloads\Desi-Finds`) and push the code:
   ```bash
   # Initialize git repository
   git init
   
   # Stage all files
   git add .
   
   # Commit changes
   git commit -m "Setup DesiFinds codebase"
   
   # Rename default branch to main
   git branch -M main
   
   # Link repository to GitHub (replace with your repo URL)
   git remote add origin https://github.com/YOUR_GITHUB_USERNAME/desi-finds.git
   
   # Push files
   git push -u origin main
   ```

---

## 🐍 Step 2: Deploy Backend to Render (Free Tier)

Render reads our [render.yaml](file:///c:/Users/Bhagya%20B/Downloads/Desi-Finds/render.yaml) file to set up the Python FastAPI environment automatically.

1. Sign up for a free account at [render.com](https://render.com).
2. Connect your GitHub account.
3. On the dashboard, click **New +** > **Blueprint**.
4. Select your `desi-finds` repository.
5. Give your blueprint a group name (e.g. `desifinds-stack`).
6. Under Environment Variables:
   - Input your `OPENAI_API_KEY` (if you want search AI features enabled).
   - If not using OpenAI, leave it blank; the app will default to local keyword matching automatically.
7. Click **Apply**.
8. Render will compile your Docker container. Once the deploy succeeds, Render will give you a public URL for your backend, like:
   `https://desifinds-backend-xxxx.onrender.com`

---

## 🔗 Step 3: Link Vercel to Your Render Backend

We must tell Vercel to forward all `/api` requests to your new Render server.

1. Open [vercel.json](file:///c:/Users/Bhagya%20B/Downloads/Desi-Finds/vercel.json) in your project root.
2. Replace `"https://your-desi-finds-backend.onrender.com/api/:path*"` on line 6 with your actual Render URL, for example:
   ```json
   {
     "cleanUrls": true,
     "rewrites": [
       {
         "source": "/api/:path*",
         "destination": "https://desifinds-backend-xxxx.onrender.com/api/:path*"
       },
       {
         "source": "/(.*)",
         "destination": "/index.html"
       }
     ]
   }
   ```
3. Save, commit, and push this change to GitHub:
   ```bash
   git add vercel.json
   git commit -m "Update vercel proxy destination URL"
   git push
   ```

---

## 🎨 Step 4: Deploy Frontend to Vercel (Free Tier)

Vercel will build and serve your React client.

1. Go to [vercel.com](https://vercel.com) and sign up using your GitHub account.
2. Click **Add New** > **Project**.
3. Import your `desi-finds` repository.
4. On the configuration screen, click **Edit** next to **Root Directory** and select the **`frontend`** folder (since our React app code is contained there).
5. Open the **Build and Development Settings** dropdown:
   - **Framework Preset**: Select **Vite** (Vercel should auto-detect this).
   - **Build Command**: `pnpm run build`
   - **Output Directory**: `dist/public` (Vercel builds client files inside `frontend/dist/public`).
6. Open the **Environment Variables** dropdown and add:
   - `PORT` = `3000`
   - `BASE_PATH` = `/`
7. Click **Deploy**!

Once the build finishes (usually in under a minute), Vercel will provide you with a live domain link (e.g. `https://desi-finds-xxxx.vercel.app`). Open it, sign up/login, and enjoy your live application!
