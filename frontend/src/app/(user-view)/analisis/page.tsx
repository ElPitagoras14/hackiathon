"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { useCompany } from "@/providers/company-provider";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Sheet,
  SheetContent,
} from "@/components/ui/sheet";
import {
  CheckCircle,
  XCircle,
  Calendar,
  DollarSign,
  FileText,
  AlertTriangle,
  TrendingDown,
  Clock,
} from "lucide-react";

/* ===========================
   MOCKS
   =========================== */
const USE_MOCKS = true;

// helper fecha ISO restando días
const daysAgo = (n: number) => {
  const d = new Date();
  d.setDate(d.getDate() - n);
  return d.toISOString();
};

// “BD” en memoria por company_id
const MOCK_DB: Record<
  string,
  Array<{
    id: string | number;
    company_id: number | string;
    amount: number;
    status: "APPROVED" | "REJECTED" | "PENDING";
    reason?: string | null;
    created_at: string; // ISO
  }>
> = {
  "1": [
    {
      id: "CR-001",
      company_id: 1,
      amount: 50000,
      status: "APPROVED",
      created_at: daysAgo(30),
    },
    {
      id: "CR-002",
      company_id: 1,
      amount: 120000,
      status: "REJECTED",
      reason:
        "Insuficiente historial crediticio. Requiere al menos 24 meses con entidades financieras.",
      created_at: daysAgo(22),
    },
    {
      id: "CR-003",
      company_id: 1,
      amount: 75000,
      status: "APPROVED",
      created_at: daysAgo(18),
    },
    {
      id: "CR-004",
      company_id: 1,
      amount: 200000,
      status: "REJECTED",
      reason:
        "Ratio de endeudamiento 78% supera el máximo permitido (65%) para este monto.",
      created_at: daysAgo(9),
    },
    {
      id: "CR-005",
      company_id: 1,
      amount: 30000,
      status: "PENDING",
      created_at: daysAgo(2),
    },
  ],
  "2": [
    {
      id: "CR-101",
      company_id: 2,
      amount: 90000,
      status: "APPROVED",
      created_at: daysAgo(15),
    },
    {
      id: "CR-102",
      company_id: 2,
      amount: 180000,
      status: "REJECTED",
      reason: "Flujo de caja negativo últimos 3 meses.",
      created_at: daysAgo(7),
    },
  ],
};

/* ===========================
   Tipos y helpers
   =========================== */
type UiStatus = "aprobado" | "denegado" | "pendiente";

interface ApiCreditRequest {
  id: number | string;
  company_id?: number | string;
  amount: number;
  reason?: string | null;
  status: string;
  created_at?: string;
  createdAt?: string;
}

interface Credit {
  id: string;
  amount: number;
  status: UiStatus;
  date: string; // ISO
  reason?: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";
const COMPANIES_URL = API_BASE ? `${API_BASE}/api/company` : "/api/company";
const CREDIT_URL = API_BASE
  ? `${API_BASE}/api/company/credit-requests`
  : "/api/company/credit-requests";

const mapStatus = (s: string): UiStatus => {
  const v = (s || "").toLowerCase();
  if (v.includes("denied") || v.includes("reject") || v === "denegado")
    return "denegado";
  if (v.includes("approved") || v === "aprobado") return "aprobado";
  return "pendiente";
};

const normalize = (r: ApiCreditRequest): Credit => ({
  id: String(r.id),
  amount: Number(r.amount ?? 0),
  status: mapStatus(r.status),
  date: r.createdAt ?? r.created_at ?? new Date().toISOString(),
  reason: r.reason ?? undefined,
});

/* ===========================
   Componente
   =========================== */
export default function AnalysisPage() {
  const { data: session } = useSession();
  const token = (session as any)?.accessToken as string | undefined;

  const { selectedCompany } = useCompany();

  const [creditAmount, setCreditAmount] = useState("");
  const [credits, setCredits] = useState<Credit[]>([]);
  const [selectedCredit, setSelectedCredit] = useState<Credit | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  const handleCreditClick = (credit: Credit) => {
    setSelectedCredit(credit);
    if (credit.status === "denegado") setIsDrawerOpen(true);
  };

  const fetchCreditInfo = async () => {
    const companyId = selectedCompany?.id
      ? String(Number(selectedCompany.id))
      : undefined;

    if (!companyId) {
      setCredits([]);
      return;
    }

    // MODO MOCK
    if (USE_MOCKS) {
      // simula latencia
      await new Promise((r) => setTimeout(r, 600));
      const raw = MOCK_DB[companyId] ?? [];
      setCredits(
        raw
          .slice()
          .sort(
            (a, b) =>
              new Date(b.created_at).getTime() -
              new Date(a.created_at).getTime()
          )
          .map((r) =>
            normalize({
              id: r.id,
              company_id: r.company_id,
              amount: r.amount,
              reason: r.reason,
              status: r.status,
              created_at: r.created_at,
            })
          )
      );
      return;
    }

    // MODO API real
    if (!token) return;
    const url = new URL(
      CREDIT_URL,
      typeof window !== "undefined" ? window.location.origin : undefined
    );
    url.searchParams.set("company_id", companyId);

    const res = await fetch(url.toString(), {
      headers: {
        Accept: "application/json",
        Authorization: `Bearer ${token}`,
      },
      credentials: "include",
      cache: "no-store",
    });

    const text = await res.text();
    if (!res.ok) {
      console.warn("credit-requests failed", res.status, text);
      setCredits([]);
      return;
    }

    let body: any = {};
    try {
      body = text ? JSON.parse(text) : {};
    } catch {
      body = {};
    }

    const raw: any[] = Array.isArray(body)
      ? body
      : Array.isArray(body.items)
      ? body.items
      : Array.isArray(body.payload?.items)
      ? body.payload.items
      : [];

    setCredits(raw.map(normalize));
  };

  const handleSubmitCredit = async () => {
    const companyId = selectedCompany?.id
      ? String(Number(selectedCompany.id))
      : undefined;
    if (!companyId || !creditAmount) return;

    // MODO MOCK
    if (USE_MOCKS) {
      // simula post
      await new Promise((r) => setTimeout(r, 400));
      const newId = `CR-${Date.now().toString().slice(-6)}`;
      const newItem = {
        id: newId,
        company_id: Number(companyId),
        amount: Number(creditAmount),
        status: "PENDING" as const,
        created_at: new Date().toISOString(),
      };
      MOCK_DB[companyId] = [newItem, ...(MOCK_DB[companyId] ?? [])];
      setCreditAmount("");
      fetchCreditInfo();
      return;
    }

    // MODO API real
    if (!token) return;
    try {
      const res = await fetch(`${COMPANIES_URL}/credit-request`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          company_id: Number(companyId),
          amount: Number(creditAmount),
        }),
      });
      const txt = await res.text();
      if (!res.ok) throw new Error(txt || "Error al solicitar el crédito");
      setCreditAmount("");
      fetchCreditInfo();
    } catch (e) {
      console.error(e);
      alert("No se pudo solicitar el crédito");
    }
  };

  useEffect(() => {
    fetchCreditInfo();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedCompany?.id, token]);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Análisis de Créditos
            </h1>
            <p className="text-gray-600">
              Gestión y seguimiento de solicitudes crediticias
            </p>
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Calendar className="w-4 h-4" />
            Actualizado: {new Date().toLocaleDateString("es-ES")}
          </div>
        </div>

        <Card className="mb-6 bg-white border-gray-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg font-semibold text-gray-900">
              <DollarSign className="w-5 h-5" />
              Solicitar Crédito
            </CardTitle>
            <p className="text-sm text-gray-600">
              Ingresa el monto que deseas solicitar
            </p>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4 items-end">
              <div className="flex-1">
                <Label htmlFor="amount" className="text-gray-700">
                  Monto (S/)
                </Label>
                <Input
                  id="amount"
                  type="number"
                  placeholder="Ej: 100000"
                  className="mt-1 text-black dark:text-black border-gray-300"
                  value={creditAmount}
                  onChange={(e) => setCreditAmount(e.target.value)}
                />
              </div>
              <Button
                onClick={handleSubmitCredit}
                className="bg-gradient-to-r from-blue-600 to-green-600 hover:from-blue-700 hover:to-green-700 text-white"
                disabled={!creditAmount}
              >
                Solicitar
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white border-gray-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg font-semibold text-gray-900">
              <FileText className="w-5 h-5" />
              Historial de Créditos
            </CardTitle>
            <p className="text-sm text-gray-600">
              Solicitudes anteriores y su estado actual
            </p>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4">
              {credits.length === 0 && (
                <div className="text-sm text-gray-600">
                  Aún no hay solicitudes.
                </div>
              )}

              {credits.map((credit) => (
                <div
                  key={credit.id}
                  className={`p-4 border border-gray-200 rounded-lg transition-colors ${
                    credit.status === "denegado"
                      ? "cursor-pointer hover:bg-gray-50"
                      : ""
                  }`}
                  onClick={() => handleCreditClick(credit)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {credit.status === "aprobado" ? (
                        <CheckCircle className="w-6 h-6 text-green-600" />
                      ) : credit.status === "denegado" ? (
                        <XCircle className="w-6 h-6 text-red-600" />
                      ) : (
                        <Clock className="w-6 h-6 text-blue-600" />
                      )}
                      <div>
                        <p className="font-semibold text-gray-900">
                          S/ {Number(credit.amount).toLocaleString("es-PE")}
                        </p>
                        <p className="text-sm text-gray-600">
                          Fecha:{" "}
                          {new Date(credit.date).toLocaleDateString("es-ES")}
                        </p>
                        {credit.status === "denegado" && credit.reason && (
                          <p className="text-xs text-red-700 mt-1 line-clamp-1">
                            Motivo: {credit.reason}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge
                        className={
                          credit.status === "aprobado"
                            ? "bg-green-100 text-green-800 hover:bg-green-100"
                            : credit.status === "denegado"
                            ? "bg-red-100 text-red-800 hover:bg-red-100"
                            : "bg-yellow-100 text-yellow-800 hover:bg-yellow-100"
                        }
                      >
                        {credit.status === "pendiente"
                          ? "Pendiente"
                          : credit.status === "aprobado"
                          ? "Aprobado"
                          : "Denegado"}
                      </Badge>
                    </div>
                  </div>
                  {credit.status === "denegado" && (
                    <div className="mt-2 text-sm text-gray-600 flex items-center gap-1">
                      <AlertTriangle className="w-4 h-4 text-red-600" />
                      Haz clic para ver motivo de rechazo
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Sheet open={isDrawerOpen} onOpenChange={setIsDrawerOpen}>
          <SheetContent
            side="right"
            className="p-0 w-[400px] sm:w-[560px] bg-white text-gray-900 dark:bg-neutral-900 dark:text-gray-100 shadow-xl"
          >
            {selectedCredit && selectedCredit.status === "denegado" && (
              <div className="flex h-full flex-col">
                <div className="sticky top-0 z-10 border-b border-gray-200 bg-red-50 dark:bg-red-950/20">
                  <div className="px-6 py-5">
                    <div className="flex items-center gap-3">
                      <XCircle className="w-6 h-6 text-red-600" />
                      <h2 className="text-lg font-semibold text-red-800 dark:text-red-300">
                        Crédito Denegado
                      </h2>
                    </div>
                    <p className="mt-1 text-sm text-red-700 dark:text-red-300/80">
                      {selectedCredit.reason || "Sin motivo especificado"}
                    </p>
                  </div>
                </div>

                <div className="flex-1 overflow-y-auto px-6 py-6">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs uppercase tracking-wide text-gray-600 dark:text-gray-400">
                        Código
                      </p>
                      <p className="mt-1 font-medium">{selectedCredit.id}</p>
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-wide text-gray-600 dark:text-gray-400">
                        Monto
                      </p>
                      <p className="mt-1 font-medium">
                        S/{" "}
                        {Number(selectedCredit.amount).toLocaleString("es-PE")}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-wide text-gray-600 dark:text-gray-400">
                        Fecha
                      </p>
                      <p className="mt-1 font-medium">
                        {new Date(selectedCredit.date).toLocaleDateString(
                          "es-ES"
                        )}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-wide text-gray-600 dark:text-gray-400">
                        Estado
                      </p>
                      <div className="mt-1">
                        <Badge className="bg-red-100 text-red-800">
                          Denegado
                        </Badge>
                      </div>
                    </div>
                  </div>

                  {selectedCredit.reason && (
                    <div className="mt-6">
                      <h3 className="text-sm font-medium">
                        Motivo del rechazo
                      </h3>
                      <p className="mt-2 text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                        {selectedCredit.reason}
                      </p>
                    </div>
                  )}

                  <div className="my-6 h-px bg-gray-200 dark:bg-gray-800" />

                  <div>
                    <h3 className="text-sm font-medium">Recomendaciones</h3>
                    <div className="mt-3 space-y-2 text-sm text-gray-700 dark:text-gray-300">
                      <div className="flex items-start gap-2">
                        <TrendingDown className="w-4 h-4 mt-0.5 text-blue-600" />
                        <span>
                          Mejora tu scoring crediticio antes de volver a
                          solicitar.
                        </span>
                      </div>
                      <div className="flex items-start gap-2">
                        <Clock className="w-4 h-4 mt-0.5 text-blue-600" />
                        <span>
                          Espera al menos 30 días antes de una nueva solicitud.
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="sticky bottom-0 z-10 border-t border-gray-200 bg-gray-50 dark:bg-neutral-950/30 px-6 py-4">
                  <div className="flex gap-3">
                    <Button
                      onClick={() => setIsDrawerOpen(false)}
                      variant="outline"
                      className="flex-1"
                    >
                      Cerrar
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </SheetContent>
        </Sheet>
      </div>
    </div>
  );
}
