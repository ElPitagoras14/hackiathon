"use client";

import { useState } from "react";
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

interface Credit {
  id: string;
  amount: number;
  status: "aprobado" | "denegado";
  date: string;
  reason?: string;
  details?: string;
}

const mockCredits: Credit[] = [
  {
    id: "CR-001",
    amount: 50000,
    status: "aprobado",
    date: "2024-10-15",
  },
  {
    id: "CR-002",
    amount: 120000,
    status: "denegado",
    date: "2024-09-22",
    reason: "Insuficiente historial crediticio",
    details:
      "La empresa no cuenta con un historial crediticio suficiente para el monto solicitado. Se requiere al menos 2 años de historial con instituciones financieras.",
  },
  {
    id: "CR-003",
    amount: 75000,
    status: "aprobado",
    date: "2024-08-10",
  },
  {
    id: "CR-004",
    amount: 200000,
    status: "denegado",
    date: "2024-07-05",
    reason: "Ratio de endeudamiento elevado",
    details:
      "El ratio de endeudamiento actual (78%) supera el límite máximo permitido (65%) para créditos de este monto. Se recomienda reducir la deuda existente antes de solicitar nuevos créditos.",
  },
  {
    id: "CR-005",
    amount: 30000,
    status: "aprobado",
    date: "2024-06-18",
  },
];

export default function AnalysisPage() {
  const [creditAmount, setCreditAmount] = useState("");
  const [selectedCredit, setSelectedCredit] = useState<Credit | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  const handleCreditClick = (credit: Credit) => {
    if (credit.status === "denegado") {
      setSelectedCredit(credit);
      setIsDrawerOpen(true);
    }
  };

  const handleSubmitCredit = () => {
    if (creditAmount) {
      alert(`Solicitud de crédito por S/ ${creditAmount} enviada`);
      setCreditAmount("");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
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
            Actualizado: 15 Nov 2024
          </div>
        </div>

        {/* Solicitar Crédito */}
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
                  value={creditAmount}
                  onChange={(e) => setCreditAmount(e.target.value)}
                  className="mt-1"
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

        {/* Historial de Créditos */}
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
              {mockCredits.map((credit) => (
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
                      ) : (
                        <XCircle className="w-6 h-6 text-red-600" />
                      )}
                      <div>
                        <p className="font-semibold text-gray-900">
                          S/ {credit.amount.toLocaleString()}
                        </p>
                        <p className="text-sm text-gray-600">
                          Código: {credit.id}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge
                        className={
                          credit.status === "aprobado"
                            ? "bg-green-100 text-green-800 hover:bg-green-100"
                            : "bg-red-100 text-red-800 hover:bg-red-100"
                        }
                      >
                        {credit.status === "aprobado" ? "Aprobado" : "Denegado"}
                      </Badge>
                      <p className="text-sm text-gray-600 mt-1">
                        {new Date(credit.date).toLocaleDateString("es-ES")}
                      </p>
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

        {/* Drawer para motivos de rechazo */}
        {/* Drawer para motivos de rechazo (mejorado) */}
        <Sheet open={isDrawerOpen} onOpenChange={setIsDrawerOpen}>
          <SheetContent
            side="right"
            className="p-0 w-[400px] sm:w-[560px] bg-white text-gray-900 dark:bg-neutral-900 dark:text-gray-100 shadow-xl"
          >
            {selectedCredit && (
              <div className="flex h-full flex-col">
                {/* Header fijo */}
                <div className="sticky top-0 z-10 border-b border-gray-200 bg-red-50 dark:bg-red-950/20">
                  <div className="px-6 py-5">
                    <div className="flex items-center gap-3">
                      <XCircle className="w-6 h-6 text-red-600" />
                      <h2 className="text-lg font-semibold text-red-800 dark:text-red-300">
                        Crédito Denegado
                      </h2>
                    </div>
                    <p className="mt-1 text-sm text-red-700 dark:text-red-300/80">
                      {selectedCredit.reason}
                    </p>
                  </div>
                </div>

                {/* Cuerpo scrollable */}
                <div className="flex-1 overflow-y-auto px-6 py-6">
                  {/* Datos clave en grid, misma jerarquía que el resto */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs uppercase tracking-wide text-gray-600 dark:text-gray-400">
                        Código de Solicitud
                      </p>
                      <p className="mt-1 font-medium text-gray-900 dark:text-gray-100">
                        {selectedCredit.id}
                      </p>
                    </div>

                    <div>
                      <p className="text-xs uppercase tracking-wide text-gray-600 dark:text-gray-400">
                        Monto Solicitado
                      </p>
                      <p className="mt-1 font-medium text-gray-900 dark:text-gray-100">
                        S/ {selectedCredit.amount.toLocaleString()}
                      </p>
                    </div>

                    <div>
                      <p className="text-xs uppercase tracking-wide text-gray-600 dark:text-gray-400">
                        Fecha de Solicitud
                      </p>
                      <p className="mt-1 font-medium text-gray-900 dark:text-gray-100">
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
                        <Badge className="bg-red-100 text-red-800 hover:bg-red-100 dark:bg-red-900/30 dark:text-red-300">
                          Denegado
                        </Badge>
                      </div>
                    </div>
                  </div>

                  {/* Detalles */}
                  {selectedCredit.details && (
                    <div className="mt-6">
                      <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100">
                        Detalles
                      </h3>
                      <p className="mt-2 text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                        {selectedCredit.details}
                      </p>
                    </div>
                  )}

                  {/* Separador */}
                  <div className="my-6 h-px bg-gray-200 dark:bg-gray-800" />

                  {/* Recomendaciones con iconos azules como en el resto */}
                  <div>
                    <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100">
                      Recomendaciones
                    </h3>
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

                {/* Footer fijo, estilo de card claro */}
                <div className="sticky bottom-0 z-10 border-t border-gray-200 bg-gray-50 dark:bg-neutral-950/30 px-6 py-4">
                  <div className="flex gap-3">
                    <Button
                      onClick={() => setIsDrawerOpen(false)}
                      variant="outline"
                      className="flex-1"
                    >
                      Cerrar
                    </Button>
                    {/* opcional: acción secundaria con el mismo gradiente del dashboard */}
                    {/* <Button className="flex-1 bg-gradient-to-r from-blue-600 to-green-600 hover:from-blue-700 hover:to-green-700 text-white">
              Ver recomendaciones personalizadas
            </Button> */}
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
