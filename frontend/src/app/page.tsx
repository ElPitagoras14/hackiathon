import Footer from "@/components/login/footer";
import Hero from "@/components/login/hero";
import HowItWorks from "@/components/login/HowItWorks";
import KeyBenefits from "@/components/login/keyBenefits";
import Header from "@/components/ui/header";

export default function Home() {
  return (
    <div>
      <Header />
      <section id="producto">
        <Hero />
      </section>

      <section id="beneficios">
        <KeyBenefits />
      </section>

      <section id="casos-uso">
        <HowItWorks />
      </section>
      
      <Footer />
    </div>
  );
}
