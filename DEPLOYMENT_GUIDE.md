# 🚀 Customer AI Portal - Deployment Guide

## 📋 Prerequisites

### Required Accounts & Services
- [x] Google Cloud Platform account
- [x] OpenAI API account  
- [x] ElevenLabs account (for voice)
- [x] Vercel account (frontend hosting)
- [x] Railway account (backend hosting)
- [x] GitHub account

### Required API Keys
```bash
# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
MAIN_SPREADSHEET_ID=your_spreadsheet_id

# OpenAI
OPENAI_API_KEY=sk-...

# ElevenLabs (optional for voice)
ELEVENLABS_API_KEY=...

# Database (optional - for production)
DATABASE_URL=postgresql://...

# Authentication
JWT_SECRET=your_jwt_secret_key
```

## 🏗️ Infrastructure Setup

### 1. Google Cloud Platform Setup

**Enable APIs:**
```bash
gcloud services enable sheets.googleapis.com
gcloud services enable drive.googleapis.com
```

**Create Service Account:**
```bash
gcloud iam service-accounts create customer-ai-portal \
    --display-name=\"Customer AI Portal Service Account\"

gcloud iam service-accounts keys create service-account.json \
    --iam-account=customer-ai-portal@your-project.iam.gserviceaccount.com
```

**Set Permissions:**
```bash
gcloud projects add-iam-policy-binding your-project-id \
    --member=\"serviceAccount:customer-ai-portal@your-project.iam.gserviceaccount.com\" \
    --role=\"roles/editor\"
```

### 2. Google Sheets Setup

**Create Master Spreadsheet with these sheets:**

**Sheet 1: Customers**
```
A: Customer_ID | B: Company_Name | C: Email | D: Phone | E: Registration_Date | F: Total_Spent | G: Last_Order_Date | H: Status
```

**Sheet 2: Orders**
```
A: Order_ID | B: Customer_ID | C: Date | D: Products | E: Quantities | F: Total_Amount | G: Status | H: Tracking | I: Notes
```

**Sheet 3: Products**
```
A: SKU | B: Product_Name | C: Category | D: Price | E: Stock_Level | F: Description | G: Compatibility | H: Image_URL
```

**Sheet 4: Interactions**
```
A: Timestamp | B: Customer_ID | C: Query_Type | D: Question | E: Response | F: Session_ID | G: Satisfaction_Score
```

**Share with Service Account:**
- Share the spreadsheet with your service account email
- Give \"Editor\" permissions

## 🖥️ Local Development Setup

### 1. Clone Repository
```bash
git clone https://github.com/KidCudi718/customer-ai-portal.git
cd customer-ai-portal
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
GOOGLE_APPLICATION_CREDENTIALS=../service-account.json
MAIN_SPREADSHEET_ID=your_spreadsheet_id
OPENAI_API_KEY=sk-your_openai_key
ELEVENLABS_API_KEY=your_elevenlabs_key
JWT_SECRET=your_jwt_secret
EOF

# Run backend
uvicorn main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd ..  # Back to root directory
npm install

# Create .env.local file
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF

# Run frontend
npm run dev
```

### 4. Test the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## ☁️ Production Deployment

### 1. Backend Deployment (Railway)

**Deploy to Railway:**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway add

# Set environment variables
railway variables set GOOGLE_APPLICATION_CREDENTIALS=\"$(cat service-account.json | base64)\"
railway variables set MAIN_SPREADSHEET_ID=\"your_spreadsheet_id\"
railway variables set OPENAI_API_KEY=\"sk-your_openai_key\"
railway variables set ELEVENLABS_API_KEY=\"your_elevenlabs_key\"
railway variables set JWT_SECRET=\"your_jwt_secret\"

# Deploy
railway up
```

**Alternative: Manual Railway Deployment**
1. Go to [Railway.app](https://railway.app)
2. Connect your GitHub repository
3. Select the `backend` folder as root
4. Add environment variables in Railway dashboard
5. Deploy automatically

### 2. Frontend Deployment (Vercel)

**Deploy to Vercel:**
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Set environment variables
vercel env add NEXT_PUBLIC_API_URL production
# Enter your Railway backend URL: https://your-app.railway.app
```

**Alternative: GitHub Integration**
1. Go to [Vercel.com](https://vercel.com)
2. Import your GitHub repository
3. Set build settings:
   - Framework: Next.js
   - Root Directory: `/` (root)
   - Build Command: `npm run build`
   - Output Directory: `.next`
4. Add environment variables
5. Deploy

### 3. Domain Setup

**Custom Domain (Optional):**
```bash
# Add custom domain in Vercel dashboard
# Update DNS records:
# CNAME: www -> your-app.vercel.app
# A: @ -> 76.76.19.61 (Vercel IP)
```

## 🔧 Configuration

### 1. Environment Variables

**Backend (.env):**
```bash
# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=service-account.json
MAIN_SPREADSHEET_ID=1abc123def456ghi789jkl
DRIVE_FOLDER_ID=1xyz789abc123def456

# AI Services
OPENAI_API_KEY=sk-proj-abc123...
ELEVENLABS_API_KEY=sk_abc123...

# Security
JWT_SECRET=your-super-secret-jwt-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Database (optional)
DATABASE_URL=postgresql://user:pass@host:port/db

# CORS
ALLOWED_ORIGINS=https://your-domain.com,http://localhost:3000

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

**Frontend (.env.local):**
```bash
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
NEXT_PUBLIC_APP_NAME=\"Customer AI Portal\"
NEXT_PUBLIC_COMPANY_NAME=\"Your Company\"
```

### 2. Google Sheets Data Structure

**Sample Customer Data:**
```csv
CUST001,Acme Electronics,john@acme.com,555-0123,2024-01-15,15750.00,2024-08-10,active
CUST002,Tech Solutions,sarah@techsol.com,555-0456,2024-02-20,8920.50,2024-08-05,active
```

**Sample Product Data:**
```csv
IP15-CASE-001,iPhone 15 Pro Clear Case,Phone Cases,12.99,150,\"Premium clear case for iPhone 15 Pro\",\"iPhone 15 Pro\",https://example.com/image1.jpg
SAM-S24-SCREEN,Samsung S24 Screen Protector,Screen Protectors,8.99,200,\"Tempered glass screen protector\",\"Samsung Galaxy S24\",https://example.com/image2.jpg
```

## 🔒 Security Configuration

### 1. API Security
```python
# backend/main.py - Add security headers
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(TrustedHostMiddleware, allowed_hosts=[\"your-domain.com\"])
app.add_middleware(HTTPSRedirectMiddleware)
```

### 2. Environment Security
```bash
# Never commit these files
echo \"*.env\" >> .gitignore
echo \"service-account.json\" >> .gitignore
echo \".env.local\" >> .gitignore
```

### 3. Google Cloud Security
```bash
# Restrict service account permissions
gcloud projects add-iam-policy-binding your-project-id \
    --member=\"serviceAccount:customer-ai-portal@your-project.iam.gserviceaccount.com\" \
    --role=\"roles/sheets.editor\"

gcloud projects add-iam-policy-binding your-project-id \
    --member=\"serviceAccount:customer-ai-portal@your-project.iam.gserviceaccount.com\" \
    --role=\"roles/drive.file\"
```

## 📊 Monitoring & Analytics

### 1. Application Monitoring
```python
# Add to backend/main.py
import logging
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.middleware(\"http\")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f\"{request.method} {request.url} - {response.status_code} - {process_time:.2f}s\")
    return response
```

### 2. Error Tracking
```bash
# Add Sentry for error tracking
pip install sentry-sdk[fastapi]
npm install @sentry/nextjs
```

### 3. Performance Monitoring
```python
# Add performance monitoring
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('request_duration_seconds', 'Request latency')
```

## 🧪 Testing

### 1. Backend Testing
```bash
cd backend
pip install pytest pytest-asyncio httpx
pytest tests/ -v
```

### 2. Frontend Testing
```bash
npm install --save-dev @testing-library/react @testing-library/jest-dom
npm test
```

### 3. Integration Testing
```bash
# Test API endpoints
curl -X POST \"https://your-backend.railway.app/auth/login\" \
  -H \"Content-Type: application/json\" \
  -d '{\"email\":\"test@example.com\",\"company_id\":\"COMP001\"}'
```

## 🚀 Go Live Checklist

### Pre-Launch
- [ ] All environment variables set
- [ ] Google Sheets properly configured
- [ ] API endpoints tested
- [ ] Frontend/backend communication working
- [ ] Authentication flow tested
- [ ] Error handling implemented
- [ ] Rate limiting configured
- [ ] Security headers added

### Launch
- [ ] Deploy backend to Railway
- [ ] Deploy frontend to Vercel
- [ ] Configure custom domain (optional)
- [ ] Set up monitoring
- [ ] Test with real customer data
- [ ] Create user documentation

### Post-Launch
- [ ] Monitor error rates
- [ ] Track performance metrics
- [ ] Gather user feedback
- [ ] Plan feature iterations
- [ ] Scale infrastructure as needed

## 📞 Support & Troubleshooting

### Common Issues

**1. Google Sheets Authentication Error:**
```bash
# Check service account permissions
gcloud iam service-accounts get-iam-policy customer-ai-portal@your-project.iam.gserviceaccount.com
```

**2. OpenAI API Rate Limits:**
```python
# Add retry logic
import backoff

@backoff.on_exception(backoff.expo, openai.RateLimitError)
async def call_openai_with_retry():
    # Your OpenAI call here
```

**3. CORS Issues:**
```python
# Update CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[\"https://your-domain.com\"],
    allow_credentials=True,
    allow_methods=[\"*\"],
    allow_headers=[\"*\"],
)
```

### Getting Help
- **Documentation:** Check API docs at `/docs`
- **Logs:** Check Railway/Vercel deployment logs
- **Issues:** Create GitHub issues for bugs
- **Support:** Contact support@your-domain.com

---

**🎉 Congratulations! Your Customer AI Portal is now live and ready to revolutionize customer service!**