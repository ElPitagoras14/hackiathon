import Footer from "@/components/login/footer";
import Hero from "@/components/login/hero";
import HowItWorks from "@/components/login/HowItWorks";
import KeyBenefits from "@/components/login/keyBenefits";
import { Button } from "@/components/ui/button";
import Header from "@/components/ui/header";
import Link from "next/link";

export default function Home() {
  return (
    <div>
      <Header />
      <Hero /> 
      <KeyBenefits />
      <HowItWorks />
      <Footer />
    </div>
  );
}
