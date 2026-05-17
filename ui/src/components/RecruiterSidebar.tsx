import Link from "next/link";
import { LayoutDashboard, Briefcase, Users, FileBarChart, BarChart3, Settings, LogOut } from "lucide-react";

const navItems = [
  { name: "Dashboard", href: "/recruiter/dashboard", icon: LayoutDashboard },
  { name: "Job Postings", href: "/recruiter/jobs", icon: Briefcase },
  { name: "Candidate Ranking", href: "/recruiter/candidates", icon: Users },
  { name: "Resume Compare", href: "/recruiter/compare", icon: FileBarChart },
  { name: "Analytics", href: "/recruiter/analytics", icon: BarChart3 },
];

export default function RecruiterSidebar() {
  return (
    <div className="w-64 h-screen bg-surface border-r border-border flex flex-col fixed left-0 top-0">
      <div className="p-6">
        <Link href="/">
          <span className="text-xl font-bold text-gradient">AI Resume</span>
        </Link>
      </div>
      
      <nav className="flex-1 px-4 py-4 space-y-1 overflow-y-auto">
        <div className="text-xs font-semibold text-muted uppercase tracking-wider mb-4 px-2">
          Recruiter Portal
        </div>
        {navItems.map((item) => (
          <Link
            key={item.name}
            href={item.href}
            className="flex items-center px-2 py-2.5 text-sm font-medium rounded-md text-foreground hover:bg-black/5 dark:hover:bg-white/10 transition-colors group"
          >
            <item.icon className="mr-3 h-5 w-5 text-muted group-hover:text-primary transition-colors" />
            {item.name}
          </Link>
        ))}
      </nav>

      <div className="p-4 border-t border-border">
        <Link
          href="/recruiter/settings"
          className="flex items-center px-2 py-2.5 text-sm font-medium rounded-md text-foreground hover:bg-black/5 dark:hover:bg-white/10 transition-colors group mb-1"
        >
          <Settings className="mr-3 h-5 w-5 text-muted group-hover:text-primary transition-colors" />
          Settings
        </Link>
        <button
          className="w-full flex items-center px-2 py-2.5 text-sm font-medium rounded-md text-error hover:bg-error/10 transition-colors group"
        >
          <LogOut className="mr-3 h-5 w-5" />
          Logout
        </button>
      </div>
    </div>
  );
}
