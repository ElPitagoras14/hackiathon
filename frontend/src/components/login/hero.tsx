"use client";

import { motion } from "framer-motion";
import { Button } from "../ui/button";
import { ArrowRight } from "lucide-react";

export default function Hero() {
  return (
    <div className="relative isolate overflow-hidden bg-background">
      <div className="mx-auto max-w-7xl px-6 py-20 lg:flex lg:items-center lg:gap-x-10 lg:px-8">
        <div className="mx-auto max-w-2xl lg:mx-0 lg:max-w-lg lg:flex-shrink-0">
          <motion.h1
            className="mt-10 text-4xl font-bold tracking-tight text-foreground sm:text-6xl"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <span className="text-gradient">
              <h1 className="text-4xl lg:text-6xl font-bold leading-tight">
                Evaluación crediticia{" "}
                <span className="text-blue-400">inteligente y justa</span>
              </h1>
            </span>
          </motion.h1>
          <motion.p
            className=" pt-4 mt-4 text-lg leading-8 text-muted-foreground"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            Revoluciona tu proceso de scoring crediticio con IA avanzada.
            Decisiones más rápidas, precisas e inclusivas que reducen el riesgo
            y amplían tu base de clientes elegibles.
          </motion.p>
          <motion.div
            className="mt-5 flex items-center gap-x-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            <Button size="lg" className="bg-blue-600 hover:bg-blue-700
              text-white">
              Comenzar ahora
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
            </motion.div>
        </div>
        <motion.div
          className="mx-auto mt-16 lg:mt-0"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
        >
          <div className="relative">
            <img
              src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/creative-SW6QDQbcVuwPgb6a2CYtYmRbsJa4k1.png"
              alt="Flowers & Saints design concept"
              width={600}
              height={600}
              className="w-[500px] rounded-2xl shadow-xl ring-1 ring-gray-900/10"
            />
          </div>
        </motion.div>
      </div>
    </div>
  );
}
