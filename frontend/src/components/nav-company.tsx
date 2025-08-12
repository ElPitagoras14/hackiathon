"use client";
import { SidebarGroup, SidebarMenu } from "@/components/ui/sidebar";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
} from "@radix-ui/react-select";
import { useCompany } from "@/providers/company-provider";

export function NavCompany() {

  const { companies, selectedCompany, setSelectedCompany, loading } = useCompany();

  if (loading) {
    return (
      <SidebarGroup>
        <SidebarMenu>
          <div className="py-4 border-b border-slate-700 animate-pulse">
            <div className="h-3 w-20 bg-slate-700 rounded mb-4"></div>
            <div className="h-10 w-full bg-slate-800 rounded"></div>
          </div>
        </SidebarMenu>
      </SidebarGroup>
    );
  }
  const handleChange = (id: string) => {
    const company = companies.find((c) => c.id === id) ?? null;
    setSelectedCompany(company);
  };

  const currentCompany = companies.find((c) => c.id === selectedCompany?.id);
  if (companies.length === 0 ) {
    return (
      <SidebarGroup>
        <SidebarMenu>
          <div className="py-4 border-b border-slate-700 px-4">
            <p className="text-slate-400 text-xs font-medium uppercase tracking-wider mb-3">
              No hay empresas registradas
            </p>
          </div>
        </SidebarMenu>
      </SidebarGroup>
    );
  }
  if (!currentCompany) {
    return (
      <SidebarGroup>
        <SidebarMenu>
          <div className="py-4 border-b border-slate-700 px-4">
            <p className="text-slate-400 text-xs font-medium uppercase tracking-wider mb-3">
              Empresa no encontrada
            </p>
          </div>
        </SidebarMenu>
      </SidebarGroup>
    );
  }

  return (
    <SidebarGroup>
      <SidebarMenu>
        <div className="py-4 border-b border-slate-700">
          <p className="text-slate-400 text-xs font-medium uppercase tracking-wider mb-3">
            EMPRESA ACTIVA
          </p>
          <Select
            value={selectedCompany?.id ?? undefined}
            onValueChange={handleChange}
          >
            <SelectTrigger className="w-full bg-slate-800 border-slate-700 text-white hover:bg-slate-700 h-auto p-3 z-10">
              <div className="flex items-center gap-3 w-full">
                <div
                  className={`w-8 h-8 rounded-lg flex items-center justify-center text-white font-semibold text-sm bg-black`}
                >
                  {currentCompany!.name.charAt(0)}
                </div>
                <div className="flex-1 text-left">
                  <p className="font-medium text-sm">{currentCompany?.name}</p>
                  <p className="text-slate-400 text-xs">
                    {selectedCompany?.name}
                  </p>
                </div>
              </div>
            </SelectTrigger>
            <SelectContent
              position="popper"
              align="start"
              className="bg-slate-800 border-slate-700 z-20 min-w-[var(--radix-select-trigger-width)] -translate-x-[2px]"
            >
              {companies.map((company) => (
                <SelectItem
                  key={company.id}
                  value={company.id!}
                  className="text-white hover:bg-slate-700 focus:bg-slate-700 p-3"
                >
                  <div className="flex items-center gap-3 py-1">
                    <div
                      className={`w-8 h-8 rounded-lg flex items-center justify-center text-white font-semibold text-sm bg-black`}
                    >
                      {company.name.charAt(0)}
                    </div>
                    <div>
                      <p className="font-medium text-sm">{company.name}</p>
                      <p className="text-slate-400 text-xs">{company.ruc}</p>
                    </div>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </SidebarMenu>
    </SidebarGroup>
  );
}
