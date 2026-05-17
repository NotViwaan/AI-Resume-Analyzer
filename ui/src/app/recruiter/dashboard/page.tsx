import { Users, Briefcase, FileBarChart, TrendingUp, Search, ArrowRight } from "lucide-react";
import Link from "next/link";

export default function RecruiterDashboard() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Recruiter Overview</h2>
          <p className="text-muted mt-1">Manage jobs and review top AI-ranked candidates.</p>
        </div>
        <Link 
          href="/recruiter/jobs/new"
          className="bg-primary text-primary-foreground hover:bg-primary/90 px-4 py-2 rounded-md font-medium flex items-center transition-colors"
        >
          <Briefcase className="mr-2 h-4 w-4" />
          Post New Job
        </Link>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <div className="p-6 bg-surface border border-border rounded-xl">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-muted">Active Jobs</p>
              <h3 className="text-3xl font-bold mt-2">8</h3>
            </div>
            <div className="p-2 bg-primary/20 text-primary rounded-lg">
              <Briefcase className="h-5 w-5" />
            </div>
          </div>
        </div>

        <div className="p-6 bg-surface border border-border rounded-xl">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-muted">Total Candidates</p>
              <h3 className="text-3xl font-bold mt-2">1,248</h3>
            </div>
            <div className="p-2 bg-success/20 text-success rounded-lg">
              <Users className="h-5 w-5" />
            </div>
          </div>
        </div>

        <div className="p-6 bg-surface border border-border rounded-xl">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-muted">Resumes Scanned</p>
              <h3 className="text-3xl font-bold mt-2">3,492</h3>
            </div>
            <div className="p-2 bg-warning/20 text-warning rounded-lg">
              <FileBarChart className="h-5 w-5" />
            </div>
          </div>
        </div>

        <div className="p-6 bg-surface border border-border rounded-xl">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-muted">Time to Hire</p>
              <h3 className="text-3xl font-bold mt-2">14d</h3>
            </div>
            <div className="p-2 bg-primary/20 text-primary rounded-lg">
              <TrendingUp className="h-5 w-5" />
            </div>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 p-6 bg-surface border border-border rounded-xl">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Top Ranked Candidates</h3>
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted" />
              <input 
                type="text" 
                placeholder="Search candidates..." 
                className="pl-9 pr-4 py-2 bg-background border border-border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
              />
            </div>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-muted uppercase bg-background">
                <tr>
                  <th className="px-4 py-3 rounded-tl-md">Candidate</th>
                  <th className="px-4 py-3">Applied Role</th>
                  <th className="px-4 py-3">Match Score</th>
                  <th className="px-4 py-3 rounded-tr-md">Action</th>
                </tr>
              </thead>
              <tbody>
                {[1, 2, 3, 4].map((i) => (
                  <tr key={i} className="border-b border-border hover:bg-black/5 dark:hover:bg-white/5">
                    <td className="px-4 py-3 font-medium">Sarah Jenkins {i}</td>
                    <td className="px-4 py-3 text-muted">Frontend Developer</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center">
                        <div className="w-full bg-background rounded-full h-2.5 mr-2 max-w-[100px]">
                          <div className="bg-success h-2.5 rounded-full" style={{ width: `${95 - i * 5}%` }}></div>
                        </div>
                        <span>{95 - i * 5}%</span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <Link href={`/recruiter/candidates/${i}`} className="text-primary hover:underline font-medium">
                        Review
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="p-6 bg-surface border border-border rounded-xl">
          <h3 className="text-lg font-semibold mb-4">Active Postings</h3>
          <div className="space-y-4">
            {["Frontend Developer", "Senior Product Manager", "UX Designer"].map((job, i) => (
              <div key={i} className="p-4 bg-background rounded-lg border border-border flex justify-between items-center">
                <div>
                  <p className="font-medium">{job}</p>
                  <p className="text-xs text-muted mt-1">{24 + i * 12} new candidates</p>
                </div>
                <Link href={`/recruiter/jobs/${i}`} className="text-muted hover:text-primary transition-colors">
                  <ArrowRight className="h-5 w-5" />
                </Link>
              </div>
            ))}
          </div>
          <Link href="/recruiter/jobs" className="block text-center text-sm text-primary font-medium mt-6 hover:underline">
            View All Jobs
          </Link>
        </div>
      </div>
    </div>
  );
}
