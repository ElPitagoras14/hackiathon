"use client";

import { useState } from "react";
import { Zap, RefreshCw, CheckCircle, DollarSign } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Badge } from "@/components/ui/badge";

export default function SimulacionPage() {
  const [ventasLevel, setVentasLevel] = useState([25]);
  const [flujoLevel, setFlujoLevel] = useState([0]);
  const [reputacionLevel, setReputacionLevel] = useState([78]);

  const [newScoring, setNewScoring] = useState(80);
  const [originalScore] = useState(72);

  const handleScenario = (scenario: string) => {
    switch (scenario) {
      case "optimista":
        setVentasLevel([30]);
        setFlujoLevel([20]);
        setReputacionLevel([85]);
        setNewScoring(85);
        break;
      case "pesimista":
        setVentasLevel([-20]);
        setFlujoLevel([-15]);
        setReputacionLevel([65]);
        setNewScoring(65);
        break;
      case "digital":
        setVentasLevel([10]);
        setFlujoLevel([5]);
        setReputacionLevel([90]);
        setNewScoring(78);
        break;
    }
  };

  const resetValues = () => {
    setVentasLevel([0]);
    setFlujoLevel([0]);
    setReputacionLevel([78]);
    setNewScoring(72);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Simulación de Escenarios
          </h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Modifica las variables clave de tu empresa y observa cómo impactan
            en tu scoring crediticio y condiciones de financiamiento
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Variables de Simulación */}
          <Card className="lg:col-span-2 bg-white border-gray-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg font-semibold text-gray-900">
                <Zap className="h-5 w-5 text-blue-600" />
                Variables de Simulación
              </CardTitle>
              <CardDescription className="text-gray-600">
                Ajusta los parámetros para ver el impacto en tiempo real
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-8">
              {/* Nivel de Ventas */}
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="font-medium text-gray-900">Nivel de Ventas</h3>
                  <Badge
                    variant="outline"
                    className="text-green-600 border-green-600"
                  >
                    +{ventasLevel[0]}%
                  </Badge>
                </div>
                <Slider
                  value={ventasLevel}
                  onValueChange={setVentasLevel}
                  max={100}
                  min={-50}
                  step={5}
                  className="mb-2"
                />
                <div className="flex justify-between text-xs text-gray-500">
                  <span>-50%</span>
                  <span>Base (100%)</span>
                  <span>+100%</span>
                </div>
              </div>

              {/* Flujo de Caja */}
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="font-medium text-gray-900">Flujo de Caja</h3>
                  <Badge
                    variant="outline"
                    className="text-gray-600 border-gray-600"
                  >
                    {flujoLevel[0]}%
                  </Badge>
                </div>
                <Slider
                  value={flujoLevel}
                  onValueChange={setFlujoLevel}
                  max={100}
                  min={-70}
                  step={5}
                  className="mb-2"
                />
                <div className="flex justify-between text-xs text-gray-500">
                  <span>-70%</span>
                  <span>Base (100%)</span>
                  <span>+100%</span>
                </div>
              </div>

              {/* Reputación Digital */}
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="font-medium text-gray-900">
                    Reputación Digital
                  </h3>
                  <Badge
                    variant="outline"
                    className="text-blue-600 border-blue-600"
                  >
                    {reputacionLevel[0]}/100
                  </Badge>
                </div>
                <Slider
                  value={reputacionLevel}
                  onValueChange={setReputacionLevel}
                  max={100}
                  min={20}
                  step={1}
                  className="mb-2"
                />
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Muy Baja</span>
                  <span>Regular</span>
                  <span>Excelente</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Nuevo Scoring */}
          <Card className="bg-white border-gray-200">
            <CardHeader className="text-center">
              <CardTitle className="text-lg font-semibold text-gray-900">
                Nuevo Scoring
              </CardTitle>
              <CardDescription className="text-gray-600">
                Puntuación actualizada
              </CardDescription>
            </CardHeader>
            <CardContent className="text-center">
              <div className="text-6xl font-bold text-green-600 mb-4">
                {newScoring}
              </div>
              <Badge className="bg-gray-900 text-white mb-6">Bajo Riesgo</Badge>

              <div className="space-y-3 text-left">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Score Original</span>
                  <span className="text-sm font-medium text-gray-900">
                    {originalScore}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Cambio</span>
                  <span className="text-sm font-medium text-green-600">
                    +{newScoring - originalScore}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Bottom Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
          {/* Escenarios Predefinidos */}
          <Card className="lg:col-span-2 bg-white border-gray-200">
            <CardHeader>
              <CardTitle className="text-lg font-semibold text-gray-900">
                Escenarios Predefinidos
              </CardTitle>
              <CardDescription className="text-gray-600">
                Prueba escenarios comunes con un clic
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <Button
                  variant="outline"
                  className="h-auto p-4 text-left bg-transparent"
                  onClick={() => handleScenario("optimista")}
                >
                  <div>
                    <div className="font-medium text-gray-900 mb-1">
                      Escenario Optimista
                    </div>
                    <div className="text-xs text-gray-600">
                      Crecimiento del 30% en ventas
                    </div>
                  </div>
                </Button>
                <Button
                  variant="outline"
                  className="h-auto p-4 text-left bg-transparent"
                  onClick={() => handleScenario("pesimista")}
                >
                  <div>
                    <div className="font-medium text-gray-900 mb-1">
                      Escenario Pesimista
                    </div>
                    <div className="text-xs text-gray-600">
                      Reducción del 20% en ventas
                    </div>
                  </div>
                </Button>
                <Button
                  variant="outline"
                  className="h-auto p-4 text-left bg-transparent"
                  onClick={() => handleScenario("digital")}
                >
                  <div>
                    <div className="font-medium text-gray-900 mb-1">
                      Mejora Digital
                    </div>
                    <div className="text-xs text-gray-600">
                      Fortalecimiento de presencia online
                    </div>
                  </div>
                </Button>
              </div>

              <Button
                variant="outline"
                className="w-full bg-transparent"
                onClick={resetValues}
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Resetear a Valores Base
              </Button>
            </CardContent>
          </Card>

          {/* Recomendación */}
          <Card className="bg-white border-gray-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg font-semibold text-gray-900">
                <DollarSign className="h-5 w-5 text-green-600" />
                Recomendación
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-sm text-gray-600 mb-1">Límite de Crédito</p>
                <p className="text-2xl font-bold text-green-600">S/ 165,625</p>
              </div>

              <div>
                <p className="text-sm text-gray-600 mb-1">Tasa de Interés</p>
                <p className="text-2xl font-bold text-blue-600">17.8% TEA</p>
              </div>

              <div>
                <p className="text-sm text-gray-600 mb-1">
                  Probabilidad de Default
                </p>
                <p className="text-2xl font-bold text-purple-600">2%</p>
              </div>

              <div className="flex items-center gap-2 pt-4">
                <CheckCircle className="h-5 w-5 text-green-600" />
                <span className="text-sm font-medium text-green-600">
                  Crédito Recomendado
                </span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
