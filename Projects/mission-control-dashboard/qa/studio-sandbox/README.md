# LINK Studio OS - Mission Control Dashboard

Internal operations dashboard for managing Money (invoices/proposals) and Social Media posting schedule with spreadsheet-style CRUD interface.

## Architecture

```
Projects/mission-control-dashboard/qa/studio-sandbox/
├── studio_os.py          # Flask backend - API server
├── index.html            # Dashboard UI structure
├── studio.css            # LINK Studio design tokens
├── studio.js             # Frontend logic + CRUD
├── requirements.txt      # Python dependencies
└── tests/               # Test suite

Company/
├── Money/
│   ├── Invoices/register.csv       # Invoice truth (CSV)
│   └── Proposals/register.csv      # Proposal truth (CSV)
├── Marketing/social/
│   ├── studio-social.json          # Social posts truth (JSON)
│   ├── 2026-09-19-posting-schedule-SEP24-OCT.md
│   └── 2026-09-19-post-drafts-REVIEW.md
└── Ops/Studio/records.json         # Ops calendar/notes

Design/
└── LINK-STUDIO-STYLE.md            # Design system tokens
```

## Data Truth Sources

### Money Registers (CSV)

**Invoices** — `Company/Money/Invoices/register.csv`
- Fields: `invoice_id`, `proposal_id`, `job_ticket`, `client_slug`, `amount`, `status`, `date_issued`, `date_due`, `date_paid`, `notes`
- Linkage: `job_ticket` + `proposal_id` link to proposals and (future) tickets

**Proposals** — `Company/Money/Proposals/register.csv`
- Fields: `proposal_id`, `job_ticket`, `lead_slug`, `client_name`, `amount`, `status`, `date_created`, `date_sent`, `date_accepted`, `scope_summary`
- Linkage: `job_ticket` links to invoices; `lead_slug` identifies client

### Social Media (JSON)

**Posts** — `Company/Marketing/social/studio-social.json`
- Structure: `{revision, posts: [{id, date, channel, type, hook, asset, cta, status, identity, draft_file}]}`
- Seeded from posting schedule and draft files
- **Draft-only:** No auto-posting. Chad reviews + manually publishes.

### Ops Records (JSON)

**Calendar/Notes** — `Company/Ops/Studio/records.json`
- Structure: `{revision, events[], notes[], channels[]}`
- Currently read-only in dashboard

## Setup

### Local Development

1. **Install Python dependencies:**
   ```bash
   cd Projects/mission-control-dashboard/qa/studio-sandbox
   pip install -r requirements.txt
   ```

2. **Verify data paths exist:**
   - Backend auto-resolves paths between `/Users/chane/Desktop/MyLINK` (Mac local) and repo structure
   - On first run, backend will create missing directories

3. **Start the server:**
   ```bash
   python studio_os.py
   ```
   Server runs on `http://localhost:8792`

4. **Open dashboard:**
   ```bash
   open http://localhost:8792
   ```

### Path Resolution

`studio_os.py` tries Mac path first, falls back to repo:
- Mac: `/Users/chane/Desktop/MyLINK/Company/Money/...`
- Repo: `/workspace/Company/Money/...`

Works seamlessly in both environments.

## Features

### Company → Money

- **Invoices spreadsheet** with full CRUD
- **Proposals spreadsheet** with full CRUD
- **Linkage visualization** via `ticket → proposal → invoice` chain
- **Status badges** (paid, sent, draft, overdue)
- **Atomic CSV writes** with `.bak` backup before every save

### Company → Social Media

**Two view modes:**

1. **Calendar View (Default)**
   - Month/week board with posts as visual cards on dates
   - Channel color coding (LinkedIn blue, Twitter light blue, Instagram pink, Facebook blue)
   - Status dots (idea=gray, draft/review=orange, Chad-ready/approved=purple, posted=green)
   - Click any post card to open inspector panel
   
2. **Spreadsheet View**
   - Dense table for bulk editing
   - Full CRUD operations
   - Quick status updates

**Inspector Panel** (profile-review style):
- Paste-ready hook and CTA text with copy buttons
- Channel and identity badges
- Asset brief and draft file links
- Quick status progression
- Edit details button
- Mobile-responsive slide-in panel

**Features:**
- **Calendar board view** with posts as visual cards on dates
- **Inspector/detail panel** (profile-review style) for paste-ready content
- **Spreadsheet toggle** for dense editing mode
- **Seeded from posting schedule** (Sep 24–Oct 31)
- **Draft file links** to markdown drafts
- **Multi-channel support** (LinkedIn, Twitter/X, Instagram)
- **Identity tracking** (Chad personal vs LINK brand)
- **Status workflow** (idea → draft → review → Chad-ready → approved → scheduled → posted)
- **Copy buttons** for easy paste of hooks and CTAs
- **Mobile-friendly** inspector panel
- **Hard constraint: Draft-only, no auto-posting**

### UI/UX

- **LINK Studio design system** (see `Design/LINK-STUDIO-STYLE.md`)
- **Dense spreadsheet layout** optimized for quick scanning
- **Visual calendar board** for social media review
- **Inline editing** via modal forms
- **Hover row highlights** for readability
- **Status color coding** for instant visual parsing

## API Endpoints

```
GET  /api/studio-os              # Full dashboard payload
GET  /api/health                 # Health check

GET  /api/money/invoices         # List invoices
POST /api/money/invoices         # Create invoice (auto-ID)
PUT  /api/money/invoices         # Update invoice

GET  /api/money/proposals        # List proposals
POST /api/money/proposals        # Create proposal (auto-ID)
PUT  /api/money/proposals        # Update proposal

GET  /api/social/posts           # List posts
POST /api/social/posts           # Create post (auto-ID)
PUT  /api/social/posts           # Update post
DELETE /api/social/posts         # Delete post
```

## Testing

```bash
cd Projects/mission-control-dashboard/qa/studio-sandbox
python -m pytest tests/ -v
```

Tests cover:
- CSV read/write with backup
- JSON read/write with revision timestamps
- API endpoints (CRUD operations)
- Path resolution (Mac vs repo)
- Data integrity (field validation)

## Security & Safety

- **Atomic writes:** All CSV/JSON writes go to `.tmp` file, then replace
- **Auto-backup:** `.bak` files created before every overwrite
- **No auto-send:** Social posts are draft-only; no external API calls
- **Local-only:** Server binds to `0.0.0.0` but intended for local/studio network use

## What's Wired

✅ **Money registers** → Spreadsheet read + CRUD → CSV write-back  
✅ **Ticket/proposal/invoice linkage** → Badge display in tables  
✅ **Social posts** → Spreadsheet read + CRUD → JSON write-back  
✅ **Seeded schedule** → 6 draft posts from Sep–Oct posting plan  
✅ **LINK Studio styling** → Dense, professional, precision-first UI  

## What's Not Wired (Out of Scope)

❌ Job ticket folder integration (folders thin; linkage via CSV fields only)  
❌ Auto-posting to social platforms (hard constraint: draft-only)  
❌ Calendar/events CRUD (Ops records currently read-only)  
❌ Email notifications or reminders  

## Design Decisions

1. **CSV for Money:** Existing truth format; backward-compatible
2. **JSON for Social:** More flexible structure; easier nested data
3. **Spreadsheet UI:** Chad's requirement—"card layout not working for quick scans"
4. **Atomic writes:** Prevent corruption from crashes mid-write
5. **Path auto-resolution:** Works on Mac local + repo without config changes

## Deployment Notes

- **Port 8792** chosen per task spec
- **Flask debug mode** on by default; disable for production
- **CORS enabled** for frontend development; tighten for production
- **Single-process:** Fine for 1–2 users; use gunicorn/waitress for team use

## Troubleshooting

**Server won't start:**
- Check Python 3.8+ installed
- Verify port 8792 not in use: `lsof -i :8792`
- Install dependencies: `pip install -r requirements.txt`

**Data not loading:**
- Check API health: `curl http://localhost:8792/api/health`
- Verify CSV/JSON files exist at paths shown in health response
- Check browser console for API errors

**CSV corruption:**
- Restore from `.bak` backup in same directory
- Check field count matches header (commas in notes can break CSV)

**Changes not saving:**
- Check browser console for 400/500 errors
- Verify write permissions on CSV/JSON files
- Check server logs for Python exceptions

## Future Enhancements

- Real-time collaboration (WebSocket sync)
- Advanced filtering + search across registers
- Export to PDF/Excel for reporting
- Calendar integration (Google Calendar sync)
- Ticket folder auto-scan (when ticket structure solidifies)
- Analytics dashboard (revenue trends, posting frequency)

---

**Built:** 2026-09-20  
**Stack:** Python/Flask + Vanilla JS + LINK Studio Design System  
**Purpose:** Internal operations, not public-facing
