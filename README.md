# LINK — itsyourlink website & internal tools

This repository contains the LINK website and internal studio operations tools.

## Contents

### Mission Control Dashboard
Internal operations dashboard for managing company finances and social media.

**Location:** `Projects/mission-control-dashboard/qa/studio-sandbox/`

**Features:**
- 💰 Money management (invoices & proposals) with spreadsheet CRUD
- 📱 Social media posting schedule (draft-only, no auto-post)
- 🔗 Ticket → Proposal → Invoice linkage visualization
- 🎨 LINK Studio design system

**Quick Start:**
```bash
cd Projects/mission-control-dashboard/qa/studio-sandbox
./start.sh
# Opens on http://localhost:8792
```

**Documentation:** See [studio-sandbox/README.md](Projects/mission-control-dashboard/qa/studio-sandbox/README.md)

### Data Structure

```
Company/
├── Money/
│   ├── Invoices/register.csv       # Invoice register
│   └── Proposals/register.csv      # Proposal register
├── Marketing/social/
│   ├── studio-social.json          # Social posting schedule
│   ├── 2026-09-19-posting-schedule-SEP24-OCT.md
│   └── 2026-09-19-post-drafts-REVIEW.md
└── Ops/Studio/
    └── records.json                # Studio operations log

Design/
└── LINK-STUDIO-STYLE.md            # Design system tokens
```

## Stack

- **Backend:** Python 3.8+ / Flask
- **Frontend:** Vanilla JavaScript / CSS
- **Data:** CSV (money) + JSON (social/ops)
- **Design:** LINK Studio Design System

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/chadchaney78-spec/link.git
   cd link
   ```

2. **Install Python dependencies**
   ```bash
   cd Projects/mission-control-dashboard/qa/studio-sandbox
   pip install -r requirements.txt
   ```

3. **Run tests**
   ```bash
   python -m pytest tests/ -v
   ```

4. **Start Mission Control**
   ```bash
   ./start.sh
   # or manually:
   python studio_os.py
   ```

## Development

### Mission Control Changes

1. Make changes to `studio_os.py`, `studio.js`, `studio.css`, or `index.html`
2. Run tests: `python -m pytest tests/ -v`
3. Test locally: `python studio_os.py`
4. Commit with clear message describing the change

### Adding Data

**New Invoice/Proposal:**
- Use Mission Control UI (+ buttons)
- Or edit CSV files directly (maintain header structure)

**New Social Post:**
- Use Mission Control UI (+ Post button)
- Or edit `Company/Marketing/social/studio-social.json`

### Design Changes

Design tokens live in `Design/LINK-STUDIO-STYLE.md`. To update styling:
1. Edit tokens in the design doc
2. Update CSS variables in `studio.css` `:root` section
3. Test across all Mission Control views

## Security

- 🔒 Local-only by default (runs on localhost)
- 💾 Automatic backups (`.bak` files) before every write
- 🚫 No external API calls
- 📝 Draft-only social posts (no auto-publishing)

## Architecture Decisions

1. **CSV for Money:** Backward-compatible with existing workflows, easy to audit/export
2. **JSON for Social:** More flexible schema, easier nested data
3. **Spreadsheet UI:** Dense table layout for quick scanning (Chad's requirement)
4. **Atomic writes:** Temp file → replace to prevent corruption
5. **Path auto-resolution:** Works on Mac local (`/Users/chane/Desktop/MyLINK`) and repo paths

## Future Work

- [ ] Calendar integration (Google Calendar sync)
- [ ] Real-time collaboration (WebSocket)
- [ ] Advanced filtering & search
- [ ] Analytics dashboard (revenue trends, posting stats)
- [ ] Export to PDF/Excel
- [ ] Ticket folder auto-scan

## Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes with tests
3. Run test suite: `python -m pytest tests/ -v`
4. Commit: `git commit -m "Clear description"`
5. Push: `git push origin feature/your-feature`
6. Open PR with description + test plan

## License

Internal tool for LINK studio operations. Not for public distribution.

---

**Built:** 2026-09-20  
**Maintainer:** Chad Chaney  
**Purpose:** Internal operations management
