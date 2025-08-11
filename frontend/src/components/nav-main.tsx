"use client";
import { Building2, BarChart3, LayoutDashboard, Calculator } from "lucide-react";

import {
  SidebarGroup,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";
import Link from "next/link";
import { usePathname } from "next/navigation";

const sidebarItems = [
  { Icon: Building2, label: "Empresas", active: true },
  { Icon: BarChart3, label: "Analisis", active: false },
  { Icon: LayoutDashboard, label: "Dashboard", active: false },
  { Icon: Calculator, label: "Simulacion", active: false },
];



export function NavMain() {
  const pathname = usePathname();

  return (
    <SidebarGroup>
      <SidebarMenu>
        {sidebarItems.map(({ Icon, label }) => {
          const href = `/${label.toLowerCase()}`;
          const isActive = pathname === href;

          return (
            <SidebarMenuItem key={label}>
              <Link href={href}>
                <SidebarMenuButton
                  className={
                    isActive
                      ? "bg-blue-600 text-white hover:bg-blue-700"
                      : "text-gray-400 hover:bg-gray-800 hover:text-white"
                  }
                >
                  {Icon && <Icon className="w-5 h-5" />}
                  {label}
                </SidebarMenuButton>
              </Link>
            </SidebarMenuItem>
          );
        })}
      </SidebarMenu>
    </SidebarGroup>
  );
}