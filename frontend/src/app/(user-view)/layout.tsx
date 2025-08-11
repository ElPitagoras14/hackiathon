

import { AppSidebar } from "@/components/app-sidebar";
import { SidebarProvider } from "@/components/ui/sidebar";
import { CompanyProvider } from "@/providers/company-provider";

export default function HomeLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <>
      <SidebarProvider>
        <CompanyProvider>

          <div className="flex h-screen bg-gray-950 w-full">
            <AppSidebar />
            <main className="flex-1 overflow-auto">{children}</main>
          </div>
        </CompanyProvider>
      </SidebarProvider>
    </>
  );
}