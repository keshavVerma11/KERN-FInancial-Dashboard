# KERN Financial AI - AI Accountant

An AI-powered financial transaction processing and classification system.

## Architecture

- **Frontend**: Next.js 14 (React, TypeScript, Tailwind CSS)
- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL (via Supabase)
- **Auth**: Supabase Auth
- **AI**: Claude API (Anthropic)

## Project Structure

```
kern-financial-ai/
├── frontend/          # Next.js application
│   ├── app/          # App router pages
│   ├── components/   # React components
│   ├── lib/          # Utilities and API clients
│   └── types/        # TypeScript types
├── backend/          # FastAPI application
│   ├── app/          # Application code
│   │   ├── api/      # API routes
│   │   ├── core/     # Core config
│   │   ├── models/   # Database models
│   │   ├── services/ # Business logic
│   │   └── utils/    # Utilities
│   ├── tests/        # Test files
│   └── requirements.txt
└── docs/             # Documentation
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL (or Supabase account)
- Supabase account (free tier works)
- Claude API key (Anthropic)

### 1. Clone and Setup

```bash
git clone <your-repo>
cd kern-financial-ai
```

### 2. Supabase Setup

1. Go to https://supabase.com and create a new project
2. Note down:
   - Project URL
   - Anon/Public Key
   - JWT Secret
   - Database connection string

3. In Supabase SQL Editor, run the database setup script (see `backend/setup.sql`)

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your credentials

# Run migrations (create tables)
python -m app.db.init_db

# Start the server
uvicorn app.main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000
API docs at: http://localhost:8000/docs

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
cp .env.example .env.local
# Edit .env.local with your credentials

# Start the development server
npm run dev
```

Frontend will be available at: http://localhost:3000

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_JWT_SECRET=your-jwt-secret
ANTHROPIC_API_KEY=sk-ant-...
ENVIRONMENT=development
```

### Frontend (.env.local)
```
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Development Workflow

1. **Start backend**: `cd backend && uvicorn app.main:app --reload`
2. **Start frontend**: `cd frontend && npm run dev`
3. **Run tests**: `cd backend && pytest`

## Key Features (Roadmap)

- [x] Phase 1: Project Setup
- [ ] Phase 2: Authentication (Login/Signup)
- [ ] Phase 3: File Upload System
- [ ] Phase 4: Transaction CRUD
- [ ] Phase 5: CSV/PDF Parsing
- [ ] Phase 6: Transaction Normalization
- [ ] Phase 7: AI Classification
- [ ] Phase 8: Review Queue
- [ ] Phase 9: Income Statement Generation
- [ ] Phase 10: Balance Sheet Generation

## API Endpoints

### Auth
- `POST /api/auth/verify` - Verify JWT token

### Transactions
- `GET /api/transactions` - List all transactions
- `POST /api/transactions` - Create transaction
- `GET /api/transactions/{id}` - Get single transaction
- `PUT /api/transactions/{id}` - Update transaction
- `DELETE /api/transactions/{id}` - Delete transaction

### Documents
- `POST /api/documents/upload` - Upload financial document
- `GET /api/documents` - List uploaded documents
- `POST /api/documents/{id}/process` - Process document

### Reports
- `GET /api/reports/income-statement` - Generate P&L
- `GET /api/reports/balance-sheet` - Generate balance sheet

## Database Schema

See `backend/app/models/` for SQLAlchemy models.

Key tables:
- `users` - User accounts (synced with Supabase)
- `organizations` - Companies/clients
- `documents` - Uploaded files
- `transactions` - Financial transactions
- `categories` - Chart of accounts
- `classifications` - AI classification history

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Deployment

### Backend (Railway/Render)
1. Connect GitHub repo
2. Set environment variables
3. Deploy

### Frontend (Vercel)
1. Connect GitHub repo
2. Set environment variables
3. Deploy

## Contributing

1. Create a feature branch
2. Make your changes
3. Write tests
4. Submit a pull request

## License

MIT
