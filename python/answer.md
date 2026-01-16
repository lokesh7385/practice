# How to Deploy TestPilot to Vercel

Since your project is already on GitHub, follow these exact steps to deploy it.

### **Important Warning Before You Start**
This application currently takes **local file paths** (e.g., `C:\Users\...`) as input.
*   **On your computer (Localhost)**: It works because the server can read your hard drive.
*   **On Vercel (Cloud)**: The server **CANNOT** read your computer's hard drive.
*   **Result**: The deployed app will load, but if you try to analyze a path like `C:\MyProject`, it will say **"Path not found"**.
*   *To make it work in the cloud, the app would need to be rewritten to support File Uploads.*

---

### **Deployment Steps**

#### 1. Go to Vercel
1.  Go to [vercel.com](https://vercel.com) and **Log In**.
2.  On your dashboard, click the **"Add New..."** button (usually top right).
3.  Select **"Project"**.

#### 2. Import Repository
1.  You will see a list of your GitHub repositories.
2.  Find **TestPilot** (or your repo name).
3.  Click the **"Import"** button next to it.

#### 3. Configure Project
1.  **Framework Preset**: It might say "Other" or auto-detect Python. "Other" is fine.
2.  **Root Directory**: Leave as `./` (unless your code is in a subfolder).
3.  **Environment Variables** (Crucial):
    *   Click to expand **"Environment Variables"**.
    *   You must add your API keys here because Vercel cannot see your local `.env` or `keys.json` file.
    *   Add them one by one:
        *   **Name**: `GEMINI_API_KEY` | **Value**: `your_real_key_here` -> Click **Add**.
        *   **Name**: `GLM_API_KEY`    | **Value**: `your_real_key_here` -> Click **Add**.
        *   **Name**: `OPENROUTER_API_KEY` | **Value**: `your_real_key_here` -> Click **Add**.

#### 4. Deploy
1.  Click the **"Deploy"** button.
2.  Wait ~1-2 minutes. Vercel will install the requirements from `requirements.txt` and build the Python app.
3.  Once done, you will see a "Congratulations!" screen.
4.  Click the **screenshot** of your app to visit the live URL (e.g., `https://testpilot.vercel.app`).

### **Troubleshooting**
*   **500 Server Error**: Usually means an API key is missing or invalid. Check the "Logs" tab in Vercel.
*   **404 Not Found**: Ensure `vercel.json` is in the root of your GitHub repo.
