import CandidateSidebar from "@/components/CandidateSidebar";
import Header from "@/components/Header";

export default function CandidateLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-background flex">
      <CandidateSidebar />
      <div className="flex-1 ml-64 flex flex-col">
        <Header portalName="Candidate" />
        <main className="flex-1 p-8 overflow-y-auto">
          <div className="max-w-6xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
