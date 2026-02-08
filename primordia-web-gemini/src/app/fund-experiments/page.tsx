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
      <Section className="pt-20 pb-20">
        <div className="relative w-full max-w-[1350px] mx-auto h-[680px] bg-gray-100 rounded-[30px] overflow-hidden">
             <div className="absolute inset-0 bg-[#E5E5E5]" />
             
             <div className="relative z-10 p-16 h-full flex flex-col justify-between">
                <h1 className="font-montserrat font-bold text-78 leading-none text-black">
                  Fund Experiments
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
            <div className="bg-gray-50 rounded-[20px] p-8 h-[300px] flex flex-col border border-black/5">
                <span className="font-montserrat font-bold text-31 block mb-4">1.</span>
                <p className="font-karla text-20">Pooled donations fund small experiments that would never fit traditional grants.</p>
            </div>
            <div className="bg-gray-50 rounded-[20px] p-8 h-[300px] flex flex-col border border-black/5">
                <span className="font-montserrat font-bold text-31 block mb-4">2.</span>
                <p className="font-karla text-20">Transparent reporting through public lab notes, summaries, and showcases.</p>
            </div>
            <div className="bg-gray-50 rounded-[20px] p-8 h-[300px] flex flex-col border border-black/5">
                <span className="font-montserrat font-bold text-31 block mb-4">3.</span>
                <p className="font-karla text-20">Minimal overhead of 5% to support digital service fees.</p>
            </div>
            <div className="bg-gray-50 rounded-[20px] p-8 h-[300px] flex flex-col border border-black/5">
                <span className="font-montserrat font-bold text-31 block mb-4">4.</span>
                <p className="font-karla text-20">Option for institutions to provide matching pools allocated via community voting.</p>
            </div>
         </div>

         {/* Graphic Placeholder */}
         <div className="w-full h-[400px] bg-blue-50 rounded-[30px] flex items-center justify-center">
             <span className="font-karla text-31 opacity-30">Donation Impact Graphics (Placeholder)</span>
         </div>
      </Section>

      {/* FAQs */}
      <Section className="py-20 mb-20">
         <div className="flex gap-12">
            <h2 className="font-montserrat font-bold text-78 leading-none shrink-0">FAQs</h2>
            <FAQAccordion />
         </div>
      </Section>

      <Footer />
    </main>
  );
}
