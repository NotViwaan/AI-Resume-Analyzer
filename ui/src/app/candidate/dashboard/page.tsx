import { Upload, FileSearch, ArrowRight, Activity, CheckCircle2 } from "lucide-react";
import Link from "next/link";

export default function CandidateDashboard() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
          <p className="text-muted mt-1">Welcome back, John! Here's your resume status.</p>
        </div>
        <Link 
          href="/candidate/upload"
          className="bg-primary text-primary-foreground hover:bg-primary/90 px-4 py-2 rounded-md font-medium flex items-center transition-colors"
        >
          <Upload className="mr-2 h-4 w-4" />
          Upload New Resume
        </Link>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <div className="p-6 bg-surface border border-border rounded-xl">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-muted">Latest ATS Score</p>
              <h3 className="text-3xl font-bold mt-2">84/100</h3>
            </div>
            <div className="p-2 bg-success/20 text-success rounded-lg">
              <CheckCircle2 className="h-5 w-5" />
            </div>
          </div>
          <p className="text-sm text-success mt-4">↑ 12 points from last version</p>
        </div>

        <div className="p-6 bg-surface border border-border rounded-xl">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-muted">Resumes Analyzed</p>
              <h3 className="text-3xl font-bold mt-2">3</h3>
            </div>
            <div className="p-2 bg-primary/20 text-primary rounded-lg">
              <FileSearch className="h-5 w-5" />
            </div>
          </div>
          <p className="text-sm text-muted mt-4">Last analysis: 2 days ago</p>
        </div>

        <div className="p-6 bg-surface border border-border rounded-xl">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-muted">Profile Views</p>
              <h3 className="text-3xl font-bold mt-2">12</h3>
            </div>
            <div className="p-2 bg-warning/20 text-warning rounded-lg">
              <Activity className="h-5 w-5" />
            </div>
          </div>
          <p className="text-sm text-muted mt-4">By recruiters this week</p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <div className="p-6 bg-surface border border-border rounded-xl">
          <h3 className="text-lg font-semibold mb-4">Recent Analysis</h3>
          <div className="space-y-4">
            {[1, 2].map((i) => (
              <div key={i} className="flex items-center justify-between p-4 bg-background rounded-lg border border-border">
                <div className="flex items-center gap-4">
                  <div className="h-10 w-10 bg-primary/10 rounded-full flex items-center justify-center text-primary font-bold">
                    v{3 - i}
                  </div>
                  <div>
                    <p className="font-medium">Software Engineer Resume</p>
                    <p className="text-sm text-muted">Uploaded Oct 24, 2026</p>
                  </div>
                </div>
                <Link href="/candidate/analysis" className="text-primary hover:underline text-sm font-medium flex items-center">
                  View Report <ArrowRight className="ml-1 h-3 w-3" />
                </Link>
              </div>
            ))}
          </div>
        </div>

        <div className="p-6 bg-surface border border-border rounded-xl">
          <h3 className="text-lg font-semibold mb-4">Quick Improvements</h3>
          <ul className="space-y-4">
            <li className="flex items-start gap-3">
              <div className="mt-0.5 w-2 h-2 rounded-full bg-warning flex-shrink-0" />
              <p className="text-sm"><span className="font-medium text-foreground">Action Verbs:</span> Consider replacing weak verbs like "helped" with stronger ones like "spearheaded".</p>
            </li>
            <li className="flex items-start gap-3">
              <div className="mt-0.5 w-2 h-2 rounded-full bg-warning flex-shrink-0" />
              <p className="text-sm"><span className="font-medium text-foreground">Quantify Results:</span> Add more numbers to your recent project experience.</p>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
