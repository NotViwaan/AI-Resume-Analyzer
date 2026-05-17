"use client";

import { useState } from "react";
import { UploadCloud, FileText, CheckCircle2, AlertCircle } from "lucide-react";
import Link from "next/link";

export default function ResumeUpload() {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState<File | null>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Upload Resume</h2>
        <p className="text-muted mt-1">Upload your latest resume for AI analysis and ATS optimization.</p>
      </div>

      <div 
        className={`border-2 border-dashed rounded-2xl p-12 text-center transition-colors ${
          dragActive ? "border-primary bg-primary/5" : "border-border bg-surface"
        } ${file ? "bg-success/5 border-success/30" : ""}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        {file ? (
          <div className="flex flex-col items-center">
            <div className="h-16 w-16 bg-success/20 text-success rounded-full flex items-center justify-center mb-4">
              <FileText className="h-8 w-8" />
            </div>
            <h3 className="text-xl font-semibold">{file.name}</h3>
            <p className="text-muted mt-1">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
            <div className="flex gap-4 mt-6">
              <button 
                onClick={() => setFile(null)}
                className="px-4 py-2 border border-border rounded-md text-sm font-medium hover:bg-black/5 dark:hover:bg-white/5 transition-colors"
              >
                Cancel
              </button>
              <Link 
                href="/candidate/analysis"
                className="px-6 py-2 bg-primary text-primary-foreground rounded-md text-sm font-medium hover:bg-primary/90 transition-colors flex items-center"
              >
                Analyze Now <CheckCircle2 className="ml-2 h-4 w-4" />
              </Link>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center">
            <div className="h-16 w-16 bg-primary/10 text-primary rounded-full flex items-center justify-center mb-4">
              <UploadCloud className="h-8 w-8" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Drag & Drop your resume here</h3>
            <p className="text-muted mb-6">Supports PDF, DOCX, and TXT files up to 5MB.</p>
            
            <label className="cursor-pointer px-6 py-3 bg-foreground text-background rounded-full font-medium hover:scale-105 transition-transform">
              Browse Files
              <input type="file" className="hidden" accept=".pdf,.doc,.docx,.txt" onChange={handleChange} />
            </label>
          </div>
        )}
      </div>

      <div className="bg-warning/10 border border-warning/20 rounded-lg p-4 flex gap-3">
        <AlertCircle className="text-warning h-5 w-5 flex-shrink-0" />
        <div>
          <h4 className="font-semibold text-warning">Privacy Notice</h4>
          <p className="text-sm text-warning/80 mt-1">
            Your resume data is encrypted and only accessible to you and the employers you explicitly choose to share it with. We do not use your resume for training our AI models.
          </p>
        </div>
      </div>
    </div>
  );
}
