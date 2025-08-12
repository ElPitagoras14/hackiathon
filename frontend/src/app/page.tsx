import Footer from "@/components/login/footer";
import Hero from "@/components/login/hero";
import HowItWorks from "@/components/login/HowItWorks";
import KeyBenefits from "@/components/login/keyBenefits";
import Header from "@/components/ui/header";

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
