# AI Resume Analyzer

An intelligent, AI-powered resume analysis and applicant tracking system (ATS) platform. This project bridges the gap between candidates and recruiters by providing real-time AI feedback on resumes for candidates, and powerful sorting/ranking tools for recruiters.

## 🚀 Features

### Candidate Portal
- **Dashboard:** Track resume scores, total scans, and profile views over time.
- **ATS Analysis:** Get an in-depth score breakdown (Formatting, Action Verbs, Keywords) to understand exactly how ATS parsers view your resume.
- **Smart Upload:** Drag-and-drop resume upload system with immediate AI processing.
- **Actionable Feedback:** Receive specific, AI-generated suggestions to improve bullet points, quantify results, and add missing soft skills.

### Recruiter Portal
- **Dashboard:** Monitor key hiring metrics including Active Jobs, Total Candidates, and Time to Hire.
- **Candidate Ranking:** Automatically rank incoming applications against specific job descriptions using AI match scoring.
- **Job Management:** Post, edit, and track active job listings and the number of applicants.

## 💻 Tech Stack

### Frontend (`/ui`)
- **Framework:** Next.js 15 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS v4, Lucide React (Icons)
- **Features:** Fully responsive, Server Components, Custom Glassmorphism Theme

### Backend (`/ai-resume-backend`)
- **Framework:** FastAPI (Python)
- **Database:** MongoDB
- **Architecture:** RESTful API with routers for Auth, Candidates, Jobs, Resumes, and Analytics.
- **Deployment:** Docker & Docker Compose ready.

## 🛠️ Getting Started

### Prerequisites
- [Node.js](https://nodejs.org/) (v18+)
- [Python 3.10+](https://www.python.org/)
- [Docker & Docker Compose](https://www.docker.com/) (Optional, for backend)

### Running the Backend

The backend can be run easily via Docker Compose, which will spin up the FastAPI server and a MongoDB instance.

```bash
cd ai-resume-backend/ai-resume-analyzer
# Copy the example env file
cp backend/.env.example backend/.env

# Start the backend services
docker-compose up -d
```
The API will be available at `http://localhost:8000`. You can view the interactive Swagger documentation at `http://localhost:8000/docs`.

*(Alternatively, you can run the backend locally using `pip install -r requirements.txt` and `uvicorn main:app --reload` within the backend directory).*

### Running the Frontend

```bash
cd ui
# Install dependencies
npm install

# Start the development server
npm run dev
```
The application will be available at `http://localhost:3000`.

## 📁 Project Structure

```
.
├── ai-resume-backend/
│   └── ai-resume-analyzer/
│       ├── backend/             # FastAPI source code
│       │   ├── app/             # Routers, Models, Core Logic
│       │   └── tests/           # Backend Tests
│       └── docker-compose.yml   # Docker configuration
└── ui/
    ├── src/
    │   ├── app/                 # Next.js App Router (Candidate/Recruiter pages)
    │   ├── components/          # Reusable React components (Sidebars, Headers)
    │   └── lib/                 # Shared utilities (API Client)
    ├── public/                  # Static assets
    └── tailwind.config.ts       # UI styling configuration
```

## 🔒 Privacy & Security

Resume data is encrypted and securely stored. We ensure that candidates have full control over who sees their data, and resumes are strictly not used to train global AI models without explicit consent.
