import { Building2, MapPin, DollarSign, Clock, Users } from "lucide-react";
import Link from "next/link";

export default function RecruiterJobs() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Job Postings</h2>
          <p className="text-muted mt-1">Manage your active listings and review applicants.</p>
        </div>
        <button className="bg-primary text-primary-foreground hover:bg-primary/90 px-4 py-2 rounded-md font-medium transition-colors">
          Create New Job
        </button>
      </div>

      <div className="grid gap-4">
        {[
          { title: "Senior Frontend Engineer", location: "Remote", type: "Full-time", salary: "$120k - $150k", applicants: 142, status: "Active" },
          { title: "Product Manager", location: "New York, NY", type: "Hybrid", salary: "$130k - $160k", applicants: 89, status: "Active" },
          { title: "UX Designer", location: "San Francisco, CA", type: "On-site", salary: "$110k - $140k", applicants: 215, status: "Active" },
          { title: "Backend Developer", location: "Remote", type: "Contract", salary: "$80/hr", applicants: 45, status: "Paused" },
        ].map((job, i) => (
          <div key={i} className="bg-surface border border-border p-6 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-6 hover:border-primary/50 transition-colors">
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <h3 className="text-xl font-semibold">{job.title}</h3>
                <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${job.status === "Active" ? "bg-success/20 text-success" : "bg-warning/20 text-warning"}`}>
                  {job.status}
                </span>
              </div>
              
              <div className="flex flex-wrap items-center gap-4 text-sm text-muted">
                <span className="flex items-center"><MapPin className="mr-1.5 h-4 w-4" /> {job.location}</span>
                <span className="flex items-center"><Clock className="mr-1.5 h-4 w-4" /> {job.type}</span>
                <span className="flex items-center"><DollarSign className="mr-1.5 h-4 w-4" /> {job.salary}</span>
              </div>
            </div>

            <div className="flex items-center gap-6">
              <div className="text-center">
                <p className="text-2xl font-bold">{job.applicants}</p>
                <p className="text-xs text-muted flex items-center justify-center mt-1"><Users className="mr-1 h-3 w-3"/> Candidates</p>
              </div>
              <Link 
                href="/recruiter/candidates"
                className="px-4 py-2 border border-border rounded-md text-sm font-medium hover:bg-black/5 dark:hover:bg-white/5 transition-colors whitespace-nowrap"
              >
                View Candidates
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
