"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { useSession } from "next-auth/react";

export interface Company {
  id?: string;
  name: string;
  ruc?: string;
  industry?: string;
  igUrl?: string;
}

interface CompanyContextType {
  companies: Company[];
  selectedCompany: Company | null;
  setSelectedCompany: (company: Company | null) => void;
  loading: boolean;
  addCompany: (company: Company) => Promise<void>;
}

const CompanyContext = createContext<CompanyContextType | undefined>(undefined);

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? ""; // ej: http://localhost:4001
const COMPANIES_URL = API_BASE ? `${API_BASE}/api/company` : `/api/company`;
console.log("API_BASE:", COMPANIES_URL);
export function CompanyProvider({ children }: { children: React.ReactNode }) {
  const { data: session, status } = useSession();
  const token = (session as any)?.accessToken as string | undefined;
  console.log("Session token:", token);

  const [companies, setCompanies] = useState<Company[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);
  const [loading, setLoading] = useState(true);

  const canFetch = useMemo(
    () => status === "authenticated" && !!token,
    [status, token]
  );
  

  const fetchCompanies = async (signal?: AbortSignal) => {
    if (!canFetch) return;
    setLoading(true);
    try {
      const res = await fetch(COMPANIES_URL, {
        method: "GET",
        headers: {
          Accept: "application/json",
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        credentials: "include",
        signal,
      });
      console.log("Fetch response status:", res.status);
      const responseBody = await res.json();



      if (!res.ok) {
        // 401/403, etc.
        console.warn("fetch /api/company failed:", res.status);
        setCompanies([]);
        setSelectedCompany(null);
        return;
      }

      //inside payload and inside the items is the array of companies
      console.log("Response body:", responseBody);
      const data =  responseBody.payload.items;

      console.log("Fetched companies data:", data);
      // Asegúrate de que data sea un array

      const list = Array.isArray(data) ? data : data.companies ?? [];
      console.log("Parsed companies list:", list);

      setCompanies(list);

      // si ya había una seleccionada, intenta preservarla
      setSelectedCompany((prev) => {
        if (!prev) return list[0] ?? null;
        const stillThere = list.find((c: Company) => c.id === prev.id);
        return stillThere ?? list[0] ?? null;
      });
    } catch (e) {
      if ((e as any).name !== "AbortError") {
        console.error("Error fetching companies:", e);
      }
    } finally {
      setLoading(false);
    }
  };

  const addCompany = async (company: Company) => {
    console.log("Adding company:", company);
    try {
      const res = await fetch(COMPANIES_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token ?? ""}`,
        },
        credentials: "include",
        body: JSON.stringify(company),
      });
      console.log("Response status:", res.status);

      //print the response body for debugging AS json
      const responseBody = await res.json();
      console.log("Response body:", responseBody);

      if (!res.ok) {
        console.warn("Failed to create company:", res.status);
        throw new Error("Failed to create company");
      }
      // actualiza la lista de empresas haciendo un nuevo fetch
      await fetchCompanies();
    } catch (e) {
      console.error("Error creating company:", e);
      // fallback local si la API falla
      setCompanies((prev) => [...prev, company]);
      setSelectedCompany(company);
    }
  };

  useEffect(() => {
    // controla los estados de sesión
    if (status === "loading") {
      setLoading(true);
      return;
    }
    if (status === "unauthenticated") {
      setCompanies([]);
      setSelectedCompany(null);
      setLoading(false);
      return;
    }
    // authenticated
    const ac = new AbortController();
    fetchCompanies(ac.signal);
    return () => ac.abort();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [canFetch]);

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
