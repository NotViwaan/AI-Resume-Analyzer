import { CheckCircle2, XCircle, AlertTriangle, ArrowRight, Download } from "lucide-react";
import Link from "next/link";

export default function ATSAnalysis() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">ATS Analysis Report</h2>
          <p className="text-muted mt-1">Review your resume's compatibility and AI-generated suggestions.</p>
        </div>
        <button className="bg-surface border border-border hover:bg-black/5 dark:hover:bg-white/5 px-4 py-2 rounded-md font-medium flex items-center transition-colors text-sm">
          <Download className="mr-2 h-4 w-4" />
          Export PDF
        </button>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        <div className="md:col-span-1 space-y-6">
          <div className="p-6 bg-surface border border-border rounded-xl text-center">
            <div className="relative inline-flex items-center justify-center mb-4">
              <svg className="w-32 h-32 transform -rotate-90">
                <circle className="text-border" strokeWidth="12" stroke="currentColor" fill="transparent" r="50" cx="64" cy="64" />
                <circle className="text-primary" strokeWidth="12" strokeDasharray="314" strokeDashoffset={314 - (314 * 84) / 100} strokeLinecap="round" stroke="currentColor" fill="transparent" r="50" cx="64" cy="64" />
              </svg>
              <div className="absolute flex flex-col items-center justify-center">
                <span className="text-3xl font-bold">84</span>
                <span className="text-xs text-muted font-medium">/ 100</span>
              </div>
            </div>
            <h3 className="text-xl font-semibold">Great Match</h3>
            <p className="text-sm text-muted mt-2">Your resume passes basic ATS checks and is well-formatted.</p>
          </div>

          <div className="bg-surface border border-border rounded-xl overflow-hidden">
            <div className="p-4 border-b border-border font-semibold">Score Breakdown</div>
            <div className="divide-y divide-border">
              <div className="p-4 flex justify-between items-center">
                <span className="text-sm">Formatting</span>
                <span className="text-sm font-semibold text-success">95/100</span>
              </div>
              <div className="p-4 flex justify-between items-center">
                <span className="text-sm">Action Verbs</span>
                <span className="text-sm font-semibold text-warning">72/100</span>
              </div>
              <div className="p-4 flex justify-between items-center">
                <span className="text-sm">Quantifiable Results</span>
                <span className="text-sm font-semibold text-warning">68/100</span>
              </div>
              <div className="p-4 flex justify-between items-center">
                <span className="text-sm">Keyword Match</span>
                <span className="text-sm font-semibold text-success">88/100</span>
              </div>
            </div>
          </div>
        </div>

        <div className="md:col-span-2 space-y-6">
          <div className="bg-surface border border-border rounded-xl p-6">
            <h3 className="text-lg font-semibold mb-6 flex items-center">
              <AlertTriangle className="text-warning mr-2 h-5 w-5" /> 
              Critical Improvements Needed
            </h3>
            
            <div className="space-y-6">
              <div className="relative pl-6 border-l-2 border-warning pb-2">
                <div className="absolute w-3 h-3 bg-warning rounded-full -left-[7px] top-1"></div>
                <h4 className="font-medium text-base">Quantify your achievements</h4>
                <p className="text-sm text-muted mt-1">We found 5 bullet points that lack numbers or metrics. E.g. "Improved page load speed" → "Improved page load speed by 45%".</p>
                <div className="mt-3 p-3 bg-background border border-border rounded-md">
                  <p className="text-xs text-muted mb-1">AI Suggestion for line 24:</p>
                  <p className="text-sm">"Led the frontend team of 4 engineers to deliver the product 2 weeks ahead of schedule, increasing user retention by 15%."</p>
                </div>
              </div>

              <div className="relative pl-6 border-l-2 border-warning pb-2">
                <div className="absolute w-3 h-3 bg-warning rounded-full -left-[7px] top-1"></div>
                <h4 className="font-medium text-base">Missing Soft Skills</h4>
                <p className="text-sm text-muted mt-1">Based on target roles for Software Engineers, you are missing keywords like "Collaboration", "Agile", and "Cross-functional teams".</p>
              </div>
            </div>
          </div>

          <div className="bg-surface border border-border rounded-xl p-6">
            <h3 className="text-lg font-semibold mb-6 flex items-center">
              <CheckCircle2 className="text-success mr-2 h-5 w-5" /> 
              What You Did Well
            </h3>
            <ul className="space-y-3">
              <li className="flex items-start gap-3">
                <CheckCircle2 className="text-success h-5 w-5 flex-shrink-0" />
                <p className="text-sm">Excellent contact information formatting. Readily parsed by ATS.</p>
              </li>
              <li className="flex items-start gap-3">
                <CheckCircle2 className="text-success h-5 w-5 flex-shrink-0" />
                <p className="text-sm">No complex tables or columns that break ATS parsers.</p>
              </li>
              <li className="flex items-start gap-3">
                <CheckCircle2 className="text-success h-5 w-5 flex-shrink-0" />
                <p className="text-sm">Strong technical skills section with relevant, modern technologies listed.</p>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
