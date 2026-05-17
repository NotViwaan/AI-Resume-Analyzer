import { Bell, User } from "lucide-react";

export default function Header({ portalName }: { portalName: string }) {
  return (
    <header className="h-16 border-b border-border bg-background flex items-center justify-between px-8 sticky top-0 z-10">
      <div className="flex items-center gap-4">
        <h1 className="text-lg font-semibold text-foreground">
          {portalName} Portal
        </h1>
      </div>
      
      <div className="flex items-center gap-4">
        <button className="p-2 text-muted hover:text-foreground transition-colors rounded-full hover:bg-black/5 dark:hover:bg-white/10">
          <Bell className="h-5 w-5" />
        </button>
        <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold">
          <User className="h-4 w-4" />
        </div>
      </div>
    </header>
  );
}
