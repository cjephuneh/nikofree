# API Integration Guide

This document explains how the Niko Free frontend integrates with the Flask backend API.

## Configuration

### Environment Variables

Create a `.env` file in the `niko_free` directory with the following:

```env
VITE_API_URL=http://localhost:5000
```

For production:
```env
VITE_API_URL=https://api.nikofree.com
```

**Note:** Vite uses `VITE_` prefix for environment variables, not `REACT_APP_`.

## API Configuration File

Location: `src/config/api.ts`

This file contains:
- `API_BASE_URL` - Base URL for all API endpoints
- `API_ENDPOINTS` - Object containing all API endpoint paths
- `buildUrl()` - Helper function to build full URLs

Example usage:
```typescript
import { API_BASE_URL, API_ENDPOINTS } from '../config/api';

const url = `${API_BASE_URL}${API_ENDPOINTS.partner.apply}`;
// Result: http://localhost:5000/api/auth/partner/apply
```

## Services

### Partner Service

Location: `src/services/partnerService.ts`

Handles all partner-related API calls.

#### Available Functions

##### `applyAsPartner(data: PartnerApplicationData)`

Submits a partner application to the backend.

**Parameters:**
- `business_name` (string) - Business or brand name
- `email` (string) - Email address
- `phone_number` (string) - Phone number
- `location` (string) - City/location
- `category_id` (string) - Primary category ID (1-14)
- `interests` (string, optional) - JSON string of additional interests
- `signature_name` (string) - Digital signature (full name)
- `terms_accepted` (string) - Must be 'true'
- `logo` (File, optional) - Logo image file

**Returns:** Promise with application ID and status

**Example:**
```typescript
import { applyAsPartner } from '../services/partnerService';

const data = {
  business_name: 'My Event Company',
  email: 'partner@example.com',
  phone_number: '+254712345678',
  location: 'Nairobi',
  category_id: '1',
  interests: JSON.stringify(['Sports', 'Music']),
  signature_name: 'John Doe',
  terms_accepted: 'true',
  logo: logoFile, // File object
};

try {
  const result = await applyAsPartner(data);
  console.log('Application submitted:', result.application_id);
} catch (error) {
  console.error('Error:', error.message);
}
```

## Integration in Components

### BecomePartner.tsx

The partner application form has been integrated with the API:

1. **Import the service:**
```typescript
import { applyAsPartner } from '../services/partnerService';
```

2. **State management:**
```typescript
const [isSubmitting, setIsSubmitting] = useState(false);
const [submitError, setSubmitError] = useState('');
```

3. **Form submission:**
```typescript
const handleSubmit = async () => {
  setIsSubmitting(true);
  setSubmitError('');

  try {
    const applicationData = {
      business_name: formData.businessName,
      email: formData.email,
      phone_number: formData.phone,
      location: formData.location,
      category_id: formData.categories[0],
      interests: JSON.stringify(customInterests),
      signature_name: formData.signature,
      terms_accepted: 'true',
      logo: formData.logo || undefined,
    };

    await applyAsPartner(applicationData);
    setSubmitted(true);
  } catch (error) {
    setSubmitError(error.message);
  } finally {
    setIsSubmitting(false);
  }
};
```

4. **UI Features:**
- Loading spinner during submission
- Error message display
- Disabled state during submission
- Success page on completion

## Category IDs

The backend uses numeric IDs for categories:

| ID | Category Name |
|----|--------------|
| 1 | Travel |
| 2 | Sports & Fitness |
| 3 | Social Activities |
| 4 | Hobbies & Interests |
| 5 | Religious |
| 6 | Pets & Animals |
| 7 | Autofest |
| 8 | Health & Wellbeing |
| 9 | Music & Culture |
| 10 | Coaching & Support |
| 11 | Dance |
| 12 | Technology |
| 13 | Gaming |
| 14 | Shopping |

## Error Handling

All API calls should be wrapped in try-catch blocks:

```typescript
try {
  const result = await applyAsPartner(data);
  // Handle success
} catch (error) {
  // error.message contains the error from the backend
  console.error('API Error:', error.message);
}
```

Common errors:
- `400` - Validation error (missing/invalid fields)
- `409` - Conflict (email already registered)
- `500` - Server error

## CORS Configuration

The backend is configured to accept requests from:
- `http://localhost:5173` (Vite dev server)
- `http://localhost:3000` (Alternative port)

For production, update the backend's CORS settings in `config.py`:

```python
CORS_ORIGINS = ['https://nikofree.com']
```

## Testing the Integration

1. Start the Flask backend:
```bash
cd /path/to/nikofree-server
source venv/bin/activate
python app.py
```

2. Start the Vite dev server:
```bash
cd /path/to/nikofree-server/niko_free
npm run dev
```

3. Navigate to `http://localhost:5173` and test the "Become a Partner" form

4. Check the backend console for API requests

5. Verify the application in the database:
```bash
flask shell
>>> from app.models.partner import Partner
>>> Partner.query.filter_by(status='pending').all()
```

## Next Steps

Additional integrations to implement:
- User authentication (login/register)
- Event listing and search
- Ticket booking
- Payment processing
- Partner dashboard
- Admin panel

## Troubleshooting

### API not connecting
- Check that backend is running on `http://localhost:5000`
- Verify CORS is configured correctly
- Check browser console for errors
- Ensure `.env` file exists with `VITE_API_URL`

### FormData not sending correctly
- Ensure logo is a File object, not base64
- Check Content-Type is not set (browser sets it automatically for FormData)
- Verify all required fields are included

### Category ID errors
- Ensure category_id is a string ('1', not 1)
- Verify category exists in database
- Run `flask seed_db` if categories are missing

