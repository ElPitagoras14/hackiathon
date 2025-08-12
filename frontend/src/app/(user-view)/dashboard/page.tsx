"use client";
import {
  Calendar,
  TrendingUp,
  BarChart3,
  DollarSign,
  CheckCircle,
  AlertTriangle,
  TrendingDown,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { useCompany } from "@/providers/company-provider";
import { useEffect } from "react";

const riskFactors = [
  {
    title: "Estabilidad Financiera",
    value: 85,
    description: "Ratios financieros sólidos y flujo de caja estable",
    icon: TrendingUp,
  },
  {
    title: "Reputación Digital",
    value: 78,
    description: "Buena presencia online y comentarios favorables",
    icon: CheckCircle,
  },
  {
    title: "Historial Crediticio",
    value: 65,
    description: "Historial limitado pero sin incidencias negativas",
    icon: AlertTriangle,
  },
  {
    title: "Volatilidad Sectorial",
    value: 45,
    description: "Sector con alta competencia y márgenes ajustados",
    icon: TrendingDown,
  },
];

// función auxiliar para colores según valor
const getColors = (score: number) => {
  if (score >= 70)
    return {
      bg: "bg-green-100",
      text: "text-green-600",
      bar: "[&>div]:bg-green-500",
    };
  if (score >= 50)
    return {
      bg: "bg-yellow-100",
      text: "text-yellow-600",
      bar: "[&>div]:bg-yellow-500",
    };
  return { bg: "bg-red-100", text: "text-red-600", bar: "[&>div]:bg-red-500" };
};
  
export default function DashboardPage() {
    const { selectedCompany, loading } = useCompany();

    useEffect(() => {
      console.log("Selected company:", selectedCompany);
    }, [selectedCompany]);


  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Dashboard de Riesgo
            </h1>
            <p className="text-gray-600">
              Análisis de riesgo crediticio para{" "}
              {selectedCompany?.name || "tu empresa"}
            </p>
          </div>
          <div className="text-right">
            <div className="flex items-center gap-2 text-sm text-gray-600 mb-1">
              <Calendar className="h-4 w-4" />
              Actualizado: 15 Nov 2024
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* Scoring Alternativo */}
          <Card className="bg-white border-gray-200">
            <CardHeader className="text-center">
              <CardTitle className="text-lg font-semibold text-gray-900">
                Scoring
              </CardTitle>
              <CardDescription className="text-gray-600">
                Evaluación integral basada en IA
              </CardDescription>
            </CardHeader>
            <CardContent className="text-center">
              {/* Circular Progress */}
              <div className="relative w-48 h-48 mx-auto mb-6">
                <svg
                  className="w-48 h-48 transform -rotate-90"
                  viewBox="0 0 100 100"
                >
                  <circle
                    cx="50"
                    cy="50"
                    r="40"
                    stroke="#e5e7eb"
                    strokeWidth="8"
                    fill="none"
                  />
                  <circle
                    cx="50"
                    cy="50"
                    r="40"
                    stroke="#10b981"
                    strokeWidth="8"
                    fill="none"
                    strokeDasharray={`${72 * 2.51} 251.2`}
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-4xl font-bold text-green-600">72</span>
                  <span className="text-sm text-gray-600">Scoring</span>
                  <span className="text-sm text-gray-600">Alternativo</span>
                </div>
              </div>

              <div className="space-y-3 mb-6">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Bajo Riesgo</span>
                  <Badge className="bg-green-100 text-green-800">
                    Bajo Riesgo
                  </Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">
                    Probabilidad de Default
                  </span>
                  <span className="text-sm font-medium text-gray-900">
                    2.8%
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">
                    Límite Recomendado
                  </span>
                  <span className="text-sm font-medium text-gray-900">
                    S/ 150,000
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Tasa Sugerida</span>
                  <span className="text-sm font-medium text-gray-900">
                    18.5% TEA
                  </span>
                </div>
              </div>

              <Button className="w-full bg-gradient-to-r from-blue-600 to-green-600 hover:from-blue-700 hover:to-green-700 text-white">
                Simular Escenarios
              </Button>
            </CardContent>
          </Card>

          {/* Factores de Riesgo */}
          <Card className="lg:col-span-2 bg-white border-gray-200">
            <CardHeader>
              <CardTitle className="text-lg font-semibold text-gray-900">
                Factores de Riesgo
              </CardTitle>
              <CardDescription className="text-gray-600">
                Elementos que afectan tu puntuación crediticia
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {riskFactors.map(({ title, value, description, icon: Icon }) => {
                const colors = getColors(value);
                return (
                  <div key={title} className="flex items-center gap-4">
                    <div
                      className={`flex-shrink-0 w-10 h-10 ${colors.bg} rounded-lg flex items-center justify-center`}
                    >
                      <Icon className={`h-5 w-5 ${colors.text}`} />
                    </div>
                    <div className="flex-1">
                      <div className="flex justify-between items-center mb-2">
                        <h3 className="font-medium text-gray-900">{title}</h3>
                        <span className="text-sm font-medium text-gray-900">
                          {value}/100
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">
                        {description}
                      </p>
                      <Progress value={value} className={`h-2 ${colors.bar } bg-gray-200`} />
                    </div>
                  </div>
                );
              })}
            </CardContent>
          </Card>
        </div>

        {/* Bottom Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Comparativa Sectorial */}
          <Card className="bg-white border-gray-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg font-semibold text-gray-900">
                <BarChart3 className="h-5 w-5" />
                Comparativa Sectorial
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center mb-4">
                <div className="text-3xl font-bold text-blue-600 mb-1">
                  Top 25%
                </div>
                <p className="text-sm text-gray-600">de 1,247 empresas</p>
              </div>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Tu Score</span>
                  <span className="text-sm font-medium text-gray-900">72</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Promedio Sector</span>
                  <span className="text-sm font-medium text-gray-900">58</span>
                </div>
                <Progress value={72} className="h-2" />
              </div>
            </CardContent>
          </Card>

        </div>
      </div>
    </div>
  );
}
