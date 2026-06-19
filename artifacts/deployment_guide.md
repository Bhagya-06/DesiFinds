# 🚀 DesiFinds Deployment & Hosting Guide (GitHub, Hugging Face, and Vercel)

Since DesiFinds consists of a **React Frontend** and a **Python Backend (FastAPI)**, we deploy them on platforms optimized for each service:
1. **Backend**: Hugging Face Spaces (100% free, no card required) or Render.
2. **Frontend**: Vercel (100% free, no card required).

---

## 🛠️ Step 1: Push Your Code to GitHub

First, you need to save the project on GitHub so hosting platforms can pull your code.

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

## 🐍 Step 2: Deploy Backend (Choose One Option)

### 🌟 Option A: Deploy to Hugging Face Spaces (No Credit Card Required)
Hugging Face allows you to host Docker containers for free without asking for a credit card. We have created a root `Dockerfile` mapped to port `7860` specifically for this option.

1. Create a free account at [huggingface.co](https://huggingface.co/).
2. In the top right corner, click **New** > **Space**.
3. Name your space (e.g. `desifinds-api`).
4. Select **Docker** as the SDK (select the **Blank** template). Keep the Space **Public**.
5. Click **Create Space**.
6. Under **Repository Settings** or the instruction tab, get your Space Git URL. Add it as a Git remote on your local terminal and push your repository:
   ```bash
   # Add Hugging Face remote (replace with your HF repository URL)
   git remote add hf https://huggingface.co/spaces/YOUR_HF_USERNAME/desifinds-api
   
   # Push files directly to Hugging Face
   git push -u hf main --force
   ```
7. Go to the **Settings** tab of your Hugging Face Space. Scroll down to **Variables and secrets**:
   - Add a new **Secret** named `OPENAI_API_KEY` and input your OpenAI Key (if using AI chat features).
8. Once the build finishes, your backend API will be live! Your backend endpoint is:
   `https://YOUR_HF_USERNAME-desifinds-api.hf.space`

---

### 🐍 Option B: Deploy to Render (Credit Card Verification Required)
Render reads our `render.yaml` file to set up the environment automatically. Note that Render requires card details for account verification, even on their free tier.

1. Sign up for a free account at [render.com](https://render.com).
2. Connect your GitHub account.
3. Click **New +** > **Blueprint**.
4. Select your `desi-finds` repository and click **Apply**.
5. Under Environment Variables, input your `OPENAI_API_KEY`.
6. Render will compile your Docker container and give you a public URL like:
   `https://desifinds-backend-xxxx.onrender.com`

---

## 🔗 Step 3: Link Vercel to Your Deployed Backend

We must tell Vercel to forward all `/api` requests to your new backend server.

1. Open [vercel.json](file:///c:/Users/Bhagya%20B/Downloads/Desi-Finds/vercel.json) in your project root.
2. Replace the destination URL on line 6 with your actual backend URL:
   - For **Hugging Face**: Use `https://YOUR_HF_USERNAME-desifinds-api.hf.space/api/:path*`
   - For **Render**: Use `https://desifinds-backend-xxxx.onrender.com/api/:path*`
3. Save, commit, and push this change to GitHub:
   ```bash
   git add vercel.json
   git commit -m "Update API proxy URL in vercel config"
   git push
   ```

---

## 🎨 Step 4: Deploy Frontend to Vercel (No Credit Card Required)

Vercel will build and serve your React client.

1. Go to [vercel.com](https://vercel.com) and sign up using your GitHub account (completely free, no card required).
2. Click **Add New** > **Project** and import your `desi-finds` repository.
3. Configure the Project:
   - **Root Directory**: Click **Edit** and select the **`frontend`** folder.
   - **Framework Preset**: Select **Vite**.
   - **Build Command**: `pnpm run build`
   - **Output Directory**: `dist/public`
4. Under **Environment Variables**, add:
   - `PORT` = `3000`
   - `BASE_PATH` = `/`
5. Click **Deploy**!

Once finished, Vercel will provide your live domain link (e.g. `https://desi-finds-xxxx.vercel.app`).
