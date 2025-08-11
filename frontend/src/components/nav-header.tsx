"use client";
import {
  SidebarMenu,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar";
export function NavHeader() {
  const { state } = useSidebar();

  return (
    <SidebarMenu>
      <SidebarMenuItem>

        {/* Header */}
        <div className="p-6 border-b border-slate-700">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-white text-slate-900 rounded-lg flex items-center justify-center font-bold text-sm">
              AI
            </div>
            <div>
              <h1 className="font-semibold text-lg">Credit AI</h1>
              <p className="text-slate-400 text-sm">Financial Analytics</p>
            </div>
          </div>
        </div>

      </SidebarMenuItem>
    </SidebarMenu>
  );
}
