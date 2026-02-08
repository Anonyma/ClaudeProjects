import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { Section } from "@/components/Section";
import { Button } from "@/components/Button";
import { FAQAccordion } from "@/components/FAQAccordion";

export default function FundExperiments() {
  return (
    <main className="min-h-screen bg-white">
      <Navbar />

      {/* HERO SECTION */}
      <Section className="pt-[80px] pb-20">
        <div className="relative w-full max-w-[1350px] mx-auto h-[680px] rounded-[30px] overflow-hidden bg-gray-100">
             
             {/* Background Shape - Using the same one for consistency or specific one if different */}
             <div className="absolute left-[10px] top-[0px] w-[1241px] h-[638px] z-0 opacity-50">
                <img src="/images/hero-shape.png" alt="" className="w-full h-full object-cover" />
             </div>

             {/* Content */}
             <div className="relative z-10 p-16 h-full flex flex-col justify-between">
                <h1 className="font-montserrat font-bold text-[80px] leading-none text-black tracking-tighter">
                  <span className="block">Fund</span>
                  <span className="block">Experiments</span>
                </h1>

                <div className="flex flex-col items-end gap-12 mt-auto">
                    <h2 className="font-karla font-medium text-66 leading-[1.13] tracking-[-4.62px] max-w-[800px] text-right text-black">
                      Primordia turns your donations into visible experiments and community capacity, not overhead and jargon.
                    </h2>

                    <div className="flex gap-8">
                        <Button variant="primary" className="w-[336px]">Become a Donor</Button>
                        <Button variant="outline" className="w-[417px]">Partner on a Themed Round</Button>
                    </div>
                </div>
             </div>
        </div>
      </Section>

      {/* FOR DONORS & PARTNERS */}
      <Section className="py-20">
         <h2 className="font-montserrat font-bold text-78 leading-none mb-8">For Donors & Partners</h2>
         <p className="font-karla text-31 leading-tight max-w-[900px] mb-20">
            Pool your contribution with others to support concrete biology experiments in community labs.
         </p>

         {/* Steps Grid */}
         <div className="grid grid-cols-4 gap-6 mb-20">
            {[1, 2, 3, 4].map((step) => (
                <div key={step} className="bg-white rounded-[20px] p-8 h-[300px] flex flex-col border-[2.5px] border-black">
                    <span className="font-montserrat font-bold text-31 block mb-4">{step}.</span>
                    <p className="font-karla text-20 leading-relaxed">
                        {step === 1 && "Pooled donations fund small experiments that would never fit traditional grants."}
                        {step === 2 && "Transparent reporting through public lab notes, summaries, and showcases."}
                        {step === 3 && "Minimal overhead of 5% to support digital service fees."}
                        {step === 4 && "Option for institutions to provide matching pools that are allocated via community voting."}
                    </p>
                </div>
            ))}
         </div>

         {/* Graphic Placeholder */}
         <div className="w-full h-[400px] bg-gray-50 rounded-[30px] flex items-center justify-center border-[2.5px] border-black relative overflow-hidden">
             {/* Simple shapes to mimic the graphic */}
             <div className="flex gap-20 items-end">
                 <div className="flex flex-col items-center gap-4">
                     <div className="w-[150px] h-[185px] border-2 border-black rounded-xl" />
                     <span className="font-karla font-bold text-20">Experiment Grants</span>
                 </div>
                 <div className="flex flex-col items-center gap-4">
                     <div className="w-[100px] h-[200px] border-2 border-black rounded-xl" />
                     <span className="font-karla font-bold text-20">Lab Access</span>
                 </div>
                 <div className="flex flex-col items-center gap-4">
                     <div className="w-[120px] h-[80px] border-2 border-black rounded-xl" />
                     <span className="font-karla font-bold text-20">Program Ops</span>
                 </div>
             </div>
         </div>
      </Section>

      {/* FAQs */}
      <Section className="py-20 mb-20">
         <div className="flex gap-20">
            <h2 className="font-montserrat font-bold text-78 leading-none shrink-0 w-[175px]">FAQs</h2>
            <FAQAccordion />
         </div>
      </Section>

      <Footer />
    </main>
  );
}