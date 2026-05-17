import RecruiterSidebar from "@/components/RecruiterSidebar";
import Header from "@/components/Header";

export default function RecruiterLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-background flex">
      <RecruiterSidebar />
      <div className="flex-1 ml-64 flex flex-col">
        <Header portalName="Recruiter" />
        <main className="flex-1 p-8 overflow-y-auto">
          <div className="max-w-6xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
