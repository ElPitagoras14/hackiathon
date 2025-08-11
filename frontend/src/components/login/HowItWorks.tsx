"use client";

import { motion } from "framer-motion";
import { Database, Brain, FileText, TrendingUp } from "lucide-react";

const steps = [
  {
    icon: Database,
    title: "Conectar fuentes",
    description:
      "Integración automática con SCVS, redes sociales, datos bancarios y fuentes alternativas de información crediticia.",
    color: "bg-blue-100 text-blue-600",
  },
  {
    icon: Brain,
    title: "Evaluar con IA",
    description:
      "Nuestros algoritmos de machine learning analizan más de 500 variables para generar un scoring preciso.",
    color: "bg-green-100 text-green-600",
  },
  {
    icon: FileText,
    title: "Justificar scoring",
    description:
      "Explicación transparente de los factores que influyen en la decisión crediticia con total trazabilidad.",
    color: "bg-purple-100 text-purple-600",
  },
  {
    icon: TrendingUp,
    title: "Decidir y simular",
    description:
      "Toma decisiones informadas y simula diferentes escenarios para optimizar tu cartera crediticia.",
    color: "bg-orange-100 text-orange-600",
  },
];



export default function HowItWorks() {
  return (
    <section className="py-20 bg-background overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <h2 className="text-4xl font-bold text-foreground sm:text-4xl">
            Cómo funciona
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Un proceso simple y automatizado que transforma la evaluación
            crediticia
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {steps.map((step, index) => (
            <motion.div
              key={index}
              className="relative"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: index * 0.1 }}
            >
              <div className="text-center">
                <div
                  className={`inline-flex items-center justify-center w-16 h-16 rounded-full ${step.color} mb-6`}
                >
                  <step.icon className="w-8 h-8 z-10" />
                </div>
                <h3 className="text-xl font-semibold  mb-3">
                  {step.title}
                </h3>
                <p className="text-muted-foreground leading-relaxed">
                  {step.description}
                </p>
              </div>

              {index < steps.length - 1 && (
                <div className="hidden lg:block absolute top-8 left-full w-full h-0.5 bg-gray-200 transform -translate-x-27 z-0" />
              )}
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
