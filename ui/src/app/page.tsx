import Link from "next/link";
import { ArrowRight, Bot, ShieldCheck, Zap, Users } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <header className="px-6 lg:px-14 py-6 flex items-center justify-between sticky top-0 bg-background/80 backdrop-blur-md z-50 border-b border-border/50">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
            <Bot className="text-primary-foreground h-5 w-5" />
          </div>
          <span className="text-xl font-bold tracking-tight">AI Resume Analyzer</span>
        </div>
        <nav className="hidden md:flex items-center gap-8 text-sm font-medium">
          <Link href="#features" className="text-muted hover:text-foreground transition-colors">Features</Link>
          <Link href="#how-it-works" className="text-muted hover:text-foreground transition-colors">How it works</Link>
          <Link href="#pricing" className="text-muted hover:text-foreground transition-colors">Pricing</Link>
        </nav>
        <div className="flex items-center gap-4">
          <Link href="/candidate/dashboard" className="text-sm font-medium hover:text-primary transition-colors">
            Candidate Login
          </Link>
          <Link href="/recruiter/dashboard" className="text-sm font-medium bg-primary text-primary-foreground px-4 py-2 rounded-full hover:bg-primary/90 transition-colors">
            Recruiter Login
          </Link>
        </div>
      </header>

      <main className="flex-1 flex flex-col">
        {/* Hero Section */}
        <section className="px-6 lg:px-14 py-24 md:py-32 flex flex-col items-center text-center max-w-5xl mx-auto">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-medium mb-8">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
            </span>
            Now powered by advanced LLMs
          </div>
          <h1 className="text-5xl md:text-7xl font-bold tracking-tighter leading-tight mb-6">
            Optimize your resume for <br className="hidden md:block"/>
            <span className="text-gradient">the ATS era.</span>
          </h1>
          <p className="text-lg md:text-xl text-muted max-w-2xl mb-10">
            Whether you're a candidate looking to land your dream job, or a recruiter sorting through thousands of applications, our AI handles the heavy lifting.
          </p>
          <div className="flex flex-col sm:flex-row items-center gap-4 w-full sm:w-auto">
            <Link href="/candidate/upload" className="w-full sm:w-auto px-8 py-4 bg-foreground text-background rounded-full font-medium flex items-center justify-center hover:scale-105 transition-transform">
              Analyze My Resume <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
            <Link href="/recruiter/dashboard" className="w-full sm:w-auto px-8 py-4 bg-surface border border-border rounded-full font-medium flex items-center justify-center hover:bg-black/5 dark:hover:bg-white/5 transition-colors">
              I'm a Recruiter
            </Link>
          </div>
        </section>

        {/* Feature Section */}
        <section className="px-6 lg:px-14 py-24 bg-surface/50 border-y border-border" id="features">
          <div className="max-w-6xl mx-auto grid md:grid-cols-3 gap-12">
            <div className="space-y-4">
              <div className="h-12 w-12 rounded-xl bg-primary/10 flex items-center justify-center text-primary">
                <Zap className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-bold">Instant Analysis</h3>
              <p className="text-muted leading-relaxed">
                Get real-time feedback on your resume's impact, formatting, and keyword optimization tailored to your target roles.
              </p>
            </div>
            <div className="space-y-4">
              <div className="h-12 w-12 rounded-xl bg-success/10 flex items-center justify-center text-success">
                <ShieldCheck className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-bold">ATS Compatibility</h3>
              <p className="text-muted leading-relaxed">
                Ensure your resume passes through applicant tracking systems smoothly without losing critical formatting or data.
              </p>
            </div>
            <div className="space-y-4">
              <div className="h-12 w-12 rounded-xl bg-warning/10 flex items-center justify-center text-warning">
                <Users className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-bold">Smart Ranking</h3>
              <p className="text-muted leading-relaxed">
                For recruiters, automatically rank incoming applications against job descriptions to find the best talent faster.
              </p>
            </div>
          </div>
        </section>
      </main>
      
      <footer className="py-8 text-center text-sm text-muted border-t border-border">
        © 2026 AI Resume Analyzer. All rights reserved.
      </footer>
    </div>
  );
}
