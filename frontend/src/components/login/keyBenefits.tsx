"use client";

import { useRef, useEffect, useState } from "react";
import { motion, useAnimation, useMotionValue } from "framer-motion";
import { Target, Zap, Users, Shield } from "lucide-react";


const features = [
  {
    icon: Target,
    title: "Objetividad",
    description:
      "Elimina sesgos humanos con decisiones basadas en datos y algoritmos transparentes.",
    stats: "95% reducción en sesgos",
  },
  {
    icon: Zap,
    title: "Rapidez",
    description:
      "Evaluaciones en tiempo real que reducen el tiempo de aprobación de días a horas.",
    stats: "< 30 segundos promedio",
  },
  {
    icon: Users,
    title: "Inclusión financiera",
    description:
      "Amplía el acceso al crédito evaluando perfiles tradicionalmente excluidos del sistema.",
    stats: "+40% clientes elegibles",
  },
];


export default function FeatureCarousel() {
  const [width, setWidth] = useState(0);
  const carousel = useRef<HTMLDivElement>(null);
  const x = useMotionValue(0);
  const controls = useAnimation();

  useEffect(() => {
    if (carousel.current) {
      setWidth(carousel.current.scrollWidth - carousel.current.offsetWidth);
    }
  }, []);

  const handleDragEnd = () => {
    const currentX = x.get();
    if (currentX > 0) {
      controls.start({
        x: 0,
        transition: { type: "spring", stiffness: 300, damping: 30 },
      });
    } else if (currentX < -width) {
      controls.start({
        x: -width,
        transition: { type: "spring", stiffness: 300, damping: 30 },
      });
    }
  };

  return (
    <div className="py-20 bg-gradient-to-b from-background to-secondary/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="text-3xl font-bold text-center mb-12 text-foreground">
            Beneficios clave    
        </h2>
        <motion.div ref={carousel} className="cursor-grab overflow-hidden">
          <motion.div
            drag="x"
            dragConstraints={{ right: 0, left: -width }}
            whileTap={{ cursor: "grabbing" }}
            animate={controls}
            style={{ x }}
            onDragEnd={handleDragEnd}
            className="flex"
          >
            {features.map((feature, index) => (
              <motion.div
                key={index}
                className="min-w-[300px] h-[400px] p-8 m-4 bg-background rounded-3xl shadow-lg flex flex-col justify-between hover-lift transition-all duration-300 ease-in-out border-2 border-transparent hover:border-primary/10"
              >
                <div>
                  <feature.icon className="w-12 h-12 text-primary mb-4" />
                  <h3 className="text-xl font-semibold mb-2 text-foreground">
                    {feature.title}
                  </h3>
                  <p className="text-muted-foreground">{feature.description}</p>
                </div>
                <div className="mt-4">
                  <a
                    href="https://www.flowersandsaints.com.au"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary hover:underline"
                  >
                    Learn more →
                  </a>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}
