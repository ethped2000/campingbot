# CampingBot - Ontario Parks Availability Monitor

A web service to monitor Ontario Parks campground availability and notify you when sites become bookable.

## Quick Start

### Prerequisites
- Python 3.11+
- pip (Python package manager)

### Local Setup (SQLite - Fast)

1. **Clone/Setup**
   ```bash
   cd CampingBot
   ```

2. **Install Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   cd ..
   ```

3. **Run the Server**
   ```bash
   cd backend
   python main.py
   ```

4. **Open in Browser**
   ```
   http://localhost:8000
   ```

The app will create a SQLite database automatically on first run.

### Cloud Setup (PostgreSQL - For 24/7 Monitoring)

For a permanently running service, deploy to a cloud platform with the included PostgreSQL database:

1. **Create PostgreSQL Database**
   - Sign up at [Render.com](https://render.com) or [Railway.app](https://railway.app)
   - Create a new PostgreSQL database
   - Copy the connection string

2. **Create `.env` file**
   ```bash
   cp .env.example .env
   ```
   Update with your PostgreSQL connection string:
   ```
   DATABASE_URL=postgresql://user:password@host:5432/campingbot
   ```

3. **Deploy Backend**
   - Push to GitHub
   - Connect to Render/Railway
   - Set environment variables
   - Deploy

4. **Deploy Frontend**
   - Frontend files are served by the FastAPI backend
   - No separate frontend deployment needed

## API Endpoints

### Searches
- `GET /api/searches/` - List all searches
- `POST /api/searches/` - Create new search
- `DELETE /api/searches/{id}` - Delete search
- `GET /api/searches/{id}/availability` - Get availability for search

### Campgrounds
- `GET /api/campgrounds/` - List all available campgrounds

## Database Schema

### searches table
- id: Primary key
- campground_id: Reference to campgrounds
- site_type: Type of site (Tent, RV, etc.)
- check_in_date: Desired check-in date
- check_out_date: Desired check-out date
- created_at: When search was created
- status: active/inactive

### availability table
- id: Primary key
- search_id: Reference to searches
- site_id: Ontario Parks site identifier
- site_name: Name of the campsite
- date: Date availability is for
- available: Boolean availability status
- last_checked: When this was last checked

### campgrounds table
- id: Primary key
- name: Campground name
- park_id: Ontario Parks identifier
- region: Geographic region
- url: URL to booking page

## Phase 2 (Coming Soon)

- [ ] Ontario Parks web scraper integration
- [ ] Automatic availability checking
- [ ] SMS notifications via Twilio
- [ ] Email notifications
- [ ] Scheduled background jobs

## Local vs Cloud

| Feature | Local (SQLite) | Cloud (PostgreSQL) |
|---------|---|---|
| Setup Time | ~2 minutes | ~5 minutes |
| Cost | Free | Free (free tier) |
| Data Persistence | Local computer | Cloud server |
| 24/7 Monitoring | Only if computer on | Always running |
| Speed | Fast (local) | Slightly slower |

**Recommendation**: Start local for development, deploy to cloud when ready for continuous monitoring.
