# 🎬 D-ID Studio — AI Talking Head Generator

Generate realistic AI talking-head videos from text using D-ID's API with Microsoft Azure neural voices.

This repository supports **two full deployment options**:
1. 🐍 **Streamlit Web App** (deployable to **Streamlit Community Cloud** or run with `streamlit run app.py`)
2. ⚡ **Next.js Web App** (deployable to Vercel / Netlify or run with `npm run dev`)

---

## 🚀 Option 1: Deploy on Streamlit Community Cloud (GitHub)

### Step 1: Push to GitHub
1. Create a new repository on [GitHub](https://github.com/new).
2. Push this project to GitHub:
```bash
git init
git add .
git commit -m "Initial commit - D-ID Studio Streamlit App"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

### Step 2: Deploy to Streamlit Community Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io/) and log in with GitHub.
2. Click **New app**.
3. Select your repository, set **Main file path** to `app.py`.
4. Expand **Advanced settings...** and paste your D-ID API Key into **Secrets**:
```toml
D_ID_API_KEY = "your_d_id_api_key_here"
```
5. Click **Deploy!** 🎉

---

## 💻 Running the Streamlit App Locally

### Prerequisites
- Python 3.9+

### Quick Start
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment variables
cp .env.example .env.local
# Edit .env.local and add your D_ID_API_KEY=your_key_here

# 3. Launch Streamlit
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## ⚡ Option 2: Running as Next.js Web App

### Setup & Run
```bash
# 1. Install Node.js dependencies
npm install

# 2. Add API Key to .env.local
# D_ID_API_KEY=your_key_here

# 3. Start dev server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🌟 Key Features

- **Actual D-ID API Connection**: 2-step process (`POST /talks` to create, `GET /talks/{id}` to poll).
- **Microsoft Azure Voices**: Select from `en-US-JennyNeural`, `en-US-GuyNeural`, `en-US-AriaNeural`, `en-US-DavisNeural`.
- **Public Avatar URL Input**: Pre-filled with face image URL + preview and warning banner.
- **Script Textarea**: Character counter with 1,000 max length.
- **Interactive Player**: HTML5 video playback with MP4 download button.
- **Generation History**: Replay past generated videos anytime.
- **Secure Key Storage**: API Key stored in `.env.local` or Streamlit Secrets (never exposed in client code).

---

## 📁 Repository Structure

```
did-talking-head/
├── app.py                      # 🐍 Streamlit Web Application
├── requirements.txt            # Python dependencies for Streamlit Cloud
├── .streamlit/
│   ├── config.toml             # Custom theme settings
│   └── secrets.toml.example    # Secrets template for Streamlit Cloud
├── app/                        # ⚡ Next.js Web Application
│   ├── api/talks/              # Server-side D-ID API routes
│   ├── components/             # React client components
│   ├── globals.css             # Design tokens & styling
│   ├── layout.tsx              # Root layout
│   └── page.tsx                # Home page
├── .env.example                # Environment variable template
├── .gitignore                  # Git ignore rules
└── README.md                   # Setup and deployment documentation
```

## 📜 License

MIT
