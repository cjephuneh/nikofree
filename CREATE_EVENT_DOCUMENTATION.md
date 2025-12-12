# Create Event Feature Documentation

## Overview
A comprehensive 7-step wizard for partners to create events with full customization options.

## Features Implemented

### Step 1: Location Setup
- **Location Types**: Physical, Online, or Hybrid events
- **Physical Events**: 
  - Location name input
  - Map pin feature (placeholder for integration)
- **Online Events**: 
  - Event link (e.g., Zoom URL)
  - Link share timing options (immediately, 1hr, 30min, 15min before event)
- **Hybrid Events**: Both physical and online options available

### Step 2: Date & Time
- Start Date & Time
- End Date & Time
- Fully responsive date/time pickers

### Step 3: Categories & Interests
- **Closed Categories** (Multi-select):
  - Music & Concerts
  - Sports & Fitness
  - Food & Dining
  - Arts & Culture
  - Networking
  - Education
  - Technology
  - Charity
  - Business
  - Entertainment

- **Open Interests** (Custom tags, max 5):
  - Users can add custom interests
  - Tag-based interface
  - Easy removal with X button

### Step 4: Event Details
- Event Name input
- Event Photo upload with preview
- Drag-and-drop or click to upload
- Image preview with delete option

### Step 5: Description & Capacity
- **Description**:
  - Manual text input
  - **AI Generate** button for automatic description based on event details
  - Multi-line textarea

- **Attendee Capacity**:
  - Unlimited option
  - Limited option with number input

### Step 6: Pricing
- **Free Events**: Simple toggle
- **Paid Events** with flexible ticket structures:
  
  **1. Basic Ticket** (Uniform Price):
  - One price for all attendees
  - Perfect for tours, trip bookings, simple events
  - Example: "General Admission - KES 500"

  **2. Class-Based Tickets**:
  - VVIP: Premium experience with exclusive perks
  - VIP: Enhanced experience
  - Regular: Standard access
  - Each class has its own price point

  **3. Loyalty-Based Tickets**:
  - **Die Hard**: For super loyal fans (lowest price)
  - **Early Bird**: Reward early bookers
  - **Advance**: Standard advance purchase
  - **Gate Ticket**: Day-of-event pricing (highest price)

  **4. Season Tickets**:
  - **Daily Ticket**: Single day access for multi-day events
  - **Season Ticket**: Full event pass with customizable duration
  - Specify number of days (e.g., 3-Day Pass)
  - Example: "Day 1 Ticket - KES 500" vs "3-Day Pass - KES 1,200"

  **5. Time Slot Tickets**:
  - Book specific time periods
  - Perfect for workshops, training sessions, appointments
  - Maximum 8 time slots per event
  - Example: "9:00 AM - 10:00 AM Guitar Lesson - KES 200"

  **For all ticket types**:
  - Set price in KES
  - Define quantity available
  - VAT included toggle
  - Live preview of how ticket will display
  - Add/remove multiple ticket configurations

### Step 7: Hosts & Promotions
- **Event Hosts** (Max 2):
  - Search Niko Free members by username or name
  - Visual host selection with avatars
  - Preview how event will display:
    ```
    PICNICS AT NGONG HILLS
    Hosted by Anna Lane & Victor Muli
    ```
  - Hosts receive all RSVPs, bookings, and bucket lists

- **Promo Codes** (Optional):
  - Code name (e.g., EARLYBIRD)
  - Discount type: Percentage or Fixed Amount (KES)
  - Discount value
  - Maximum uses
  - Expiry date
  - Add/remove multiple promo codes

## User Flow

1. Click "Create Event" button in Partner Dashboard header
2. Complete 7 steps sequentially:
   - Navigation with Back/Next buttons
   - Progress bar shows completion percentage
   - Step indicator (Step X of 7)
3. Final step: "Submit for Approval" button
4. Event goes to approval queue
5. Automated posts after approval

## Technical Details

### Component Location
- **File**: `/src/components/partnerDashboard/CreateEvent.tsx`
- **Type**: Modal popup
- **Integration**: Partner Dashboard header button

### State Management
```typescript
interface EventFormData {
  locationType: 'physical' | 'online' | 'hybrid';
  locationName: string;
  onlineLink: string;
  linkShareTime: string;
  startDate/Time: string;
  endDate/Time: string;
  closedCategories: string[];
  openInterests: string[] (max 5);
  eventName: string;
  eventPhoto: File | null;
  description: string;
  attendeeLimit: number | null;
  isUnlimited: boolean;
  isFree: boolean;
  ticketTypes: TicketType[];
  hosts: Host[] (max 2);
  promoCodes: PromoCode[];
}

interface TicketType {
  ticketStructure: 'basic' | 'class' | 'loyalty' | 'season' | 'timeslot';
  // Class-based: classType ('vvip' | 'vip' | 'regular')
  // Loyalty-based: loyaltyType ('diehard' | 'earlybird' | 'advance' | 'gate')
  // Season-based: seasonType ('daily' | 'season'), seasonDuration (number)
  // Timeslot-based: timeslot (string, max 8 per event)
  price: number;
  quantity: number;
  vatIncluded: boolean;
}
```

### Responsive Design
- Full mobile support
- Tablet optimization
- Desktop-friendly layout
- Modal scrollable content area
- Touch-friendly controls

### Dark Mode
- Full dark mode support
- Consistent with app theme
- Auto-adapts to user preference

### Validation (Ready for Implementation)
- Required fields per step
- Date/time validation
- Price validation
- Host verification
- Image size limits (10MB)

## Future Enhancements
- Map integration for location pinning
- Real-time host search with API
- Image cropping/editing
- Multi-image upload
- Calendar integration
- Social media auto-posting setup
- Analytics preview
- Template saving for recurring events

## Usage

Partners can access the Create Event feature by:
1. Clicking the "Create Event" button (gradient blue, top right)
2. Button shows "New" on mobile, "Create Event" on desktop
3. Modal opens with step-by-step wizard

## Styling
- Brand colors: #27aae2 (primary), #1e8bb8 (hover)
- Gradient header
- Clean, modern interface
- Consistent spacing and typography
- Professional form layouts
