# Quick Start - Partner Application Integration

## Setup (One Time)

```bash
# 1. Navigate to frontend directory
cd niko_free

# 2. Create environment file
echo 'VITE_API_URL=http://localhost:5000' > .env.local

# 3. Install dependencies (if not done)
npm install
```

## Running

### Terminal 1 - Backend
```bash
cd /path/to/nikofree-server
source venv/bin/activate
python app.py
```
Backend will run on: **http://localhost:5000**

### Terminal 2 - Frontend
```bash
cd /path/to/nikofree-server/niko_free
npm run dev
```
Frontend will run on: **http://localhost:5173**

## Testing

1. Open browser: `http://localhost:5173`
2. Click "Become a Partner"
3. Fill out the 4-step form:
   - Step 1: Business name, logo, location
   - Step 2: Categories & interests
   - Step 3: Email & phone
   - Step 4: Signature & terms
4. Click "Submit Application"
5. Watch for:
   - Loading spinner
   - Success page
   - Or error message if something fails

## API Flow

```
Frontend (BecomePartner.tsx)
    ↓
Service (partnerService.ts)
    ↓
Backend (/api/auth/partner/apply)
    ↓
Database (partners table, status='pending')
    ↓
Admin Approval (via admin panel)
    ↓
Email Sent (with login credentials)
```

## Key Files

| File | Purpose |
|------|---------|
| `src/config/api.ts` | API configuration & endpoints |
| `src/services/partnerService.ts` | API call functions |
| `src/pages/BecomePartner.tsx` | Partner application form |
| `.env.local` | Environment variables (create this) |

## Category IDs

```typescript
1 = Travel
2 = Sports & Fitness
3 = Social Activities
4 = Hobbies & Interests
5 = Religious
6 = Pets & Animals
7 = Autofest
8 = Health & Wellbeing
9 = Music & Culture
10 = Coaching & Support
11 = Dance
12 = Technology
13 = Gaming
14 = Shopping
```

## Common Issues

### "Network Error"
- ✅ Check backend is running
- ✅ Verify URL in `.env.local`
- ✅ Check browser console

### "Invalid category"
- ✅ Run `flask seed_db` to add categories
- ✅ Verify category IDs are strings ('1' not 1)

### "CORS Error"
- ✅ Backend CORS is pre-configured for localhost:5173
- ✅ Check config.py if using different port

## What's Integrated

✅ Partner application form  
✅ Form validation  
✅ Logo file upload  
✅ API service layer  
✅ Loading states  
✅ Error handling  
✅ Success confirmation  

## What's Next

⏳ User authentication  
⏳ Event browsing  
⏳ Ticket booking  
⏳ Payment integration  
⏳ Partner dashboard  
⏳ Admin panel  

## Documentation

- **API_INTEGRATION.md** - Detailed integration guide
- **INTEGRATION_SUMMARY.md** - What was done
- **QUICK_START.md** - This file

## Support

Check backend API documentation:
- `API_ENDPOINTS.md` - Complete API reference
- `API_SUMMARY.md` - API overview
- `POSTMAN_GUIDE.md` - Postman collection

