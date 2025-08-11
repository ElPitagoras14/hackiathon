"use client";
import { createContext, useContext, useEffect, useState } from "react";

export interface Company {
  id: string;
  name: string;
  ruc?: string;
  industry?: string;
  igUrl?: string;
}

interface CompanyContextType {
  companies: Company[];
  selectedCompany: Company | null;
  setSelectedCompany: ( company: Company | null ) => void;
  loading: boolean;
  addCompany: (company: Company) => void;
}

const CompanyContext = createContext<CompanyContextType | undefined>(undefined);

export function CompanyProvider({ children }: { children: React.ReactNode }) {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchCompanies = async () => {
    setLoading(true);
    // Simular delay
    await new Promise((res) => setTimeout(res, 1500));

    const mockData: Company[] = [
      {
        id: "CS-001",
        name: "Inversiones SAC",
        industry: "Finance",
        ruc: "12345678901",
        igUrl: "https://instagram.com/inversiones_sac",
      },
      { id: "CS-002", name: "Tech Solutions", industry: "Technology", ruc: "10987654321", igUrl: "https://instagram.com/tech_solutions" },
    ];

    setCompanies(mockData);
    if (mockData.length > 0) {
      setSelectedCompany(mockData[0]); 
    }
    setLoading(false);
  };

  const addCompany = (company: Company) => {
    setCompanies((prev) => {
      const updated = [...prev, company];
      return updated;
    });
    setSelectedCompany(company);
  };

  useEffect(() => {
    fetchCompanies();
  }, []);

  return (
    <CompanyContext.Provider
      value={{
        companies,
        selectedCompany,
        setSelectedCompany,
        loading,
        addCompany,
      }}
    >
      {children}
    </CompanyContext.Provider>
  );
}

export function useCompany() {
  const ctx = useContext(CompanyContext);
  if (!ctx) throw new Error("useCompany debe usarse dentro de CompanyProvider");
  return ctx;
}
