import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { Section } from "@/components/Section";
import { Button } from "@/components/Button";
import { FAQAccordion } from "@/components/FAQAccordion";
import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen bg-white">
      <Navbar />

      {/* HERO SECTION */}
      <Section className="pt-20 pb-20">
        <div className="relative w-full max-w-[1350px] mx-auto h-[680px] bg-gray-100 rounded-[30px] overflow-hidden">
             {/* Background Shape Placeholder */}
             <div className="absolute inset-0 bg-[#E5E5E5]" /> 
             
             <div className="relative z-10 p-16 h-full flex flex-col justify-between">
                <h1 className="font-futura font-bold text-125 tracking-[-10px] leading-none text-black">
                  PRIMORDIA
                </h1>

                <div className="flex flex-col items-end gap-12 mt-auto">
                   <h2 className="font-karla font-medium text-66 leading-[1.13] tracking-[-4.62px] text-right max-w-[730px]">
                      Funding Early Biology Experiments in DIY Labs
                   </h2>

                   <div className="flex gap-8">
                      <div className="flex flex-col items-center gap-2">
                        <Button className="w-[294px]">Apply</Button>
                        <span className="font-karla text-20 opacity-60">Up-to $3000 for your project</span>
                      </div>
                      <div className="flex flex-col items-center gap-2">
                         <Button variant="primary" className="w-[318px]">Fund Experiments</Button>
                         <span className="font-karla text-20 opacity-60">Support with as little as $1/month</span>
                      </div>
                   </div>
                </div>
             </div>
        </div>
      </Section>

      {/* WHAT IS PRIMORDIA */}
      <Section className="py-20">
         <div className="grid grid-cols-1 md:grid-cols-2 gap-20 items-center">
             <div>
                <h2 className="font-montserrat font-bold text-78 leading-none mb-10">
                   What is<br />Primordia?
                </h2>
             </div>
             <div>
                <p className="font-karla font-normal text-31 leading-[1.48]">
                   Primordia is a microgrants program for early stage biology experiments run in community labs and other compliant spaces. We help people move ideas out of notebooks and into the lab by providing small, fast grants and a structure for sharing lab notes, results, and stories.
                </p>
             </div>
         </div>
         {/* Illustration Placeholder */}
         <div className="mt-16 w-full h-[400px] bg-blue-50 rounded-[30px]" />
      </Section>

      {/* HOW IT WORKS */}
      <Section className="py-20">
         <div className="flex justify-between items-end mb-16">
            <h2 className="font-montserrat font-bold text-78 leading-none">How it Works</h2>
            <p className="font-karla text-31 leading-tight max-w-[600px] text-right">
               Simple cycles for experiments that fit in months and micro-budgets.
            </p>
         </div>

         {/* Steps Grid */}
         <div className="grid grid-cols-5 gap-4">
            {[1, 2, 3, 4, 5].map((step) => (
                <div key={step} className="bg-gray-50 rounded-[20px] p-6 h-[460px] flex flex-col justify-between border border-black/5">
                   <div>
                      <span className="font-montserrat font-bold text-31 block mb-4">{step}.</span>
                      <h3 className="font-montserrat font-bold text-20 mb-4">STEP TITLE</h3>
                      <p className="font-karla text-20">Description text for step {step}...</p>
                   </div>
                   <div className="h-[100px] bg-gray-200 rounded-lg" />
                </div>
            ))}
         </div>
         
         <div className="flex justify-center mt-12">
            <Button className="w-[408px]">View Funded Experiments</Button>
         </div>
      </Section>

      {/* DEFINITION SECTION */}
      <Section className="py-20">
          <div className="bg-gray-100 rounded-[39px] p-20 flex items-center justify-center text-center">
             <p className="font-karla text-31 leading-[1.48] max-w-[800px]">
                In biology, a primordium is an organ or tissue in its earliest stage of development. Primordia is a collection of those beginnings. That is what this initiative exists for: many small, early experiments that can grow into something bigger.
             </p>
          </div>
      </Section>

      {/* STORIES & LAB NOTES */}
      <Section className="py-20">
         <h2 className="font-montserrat font-bold text-78 leading-none mb-4 text-center">Stories & Lab Notes</h2>
         <p className="font-karla text-31 text-center mb-16 opacity-60">Learn about DIY community bio initiatives</p>

         <div className="grid grid-cols-2 gap-8 mb-16">
            {/* Card 1 */}
            <div className="aspect-square bg-gray-50 rounded-[39px] p-8 relative">
               <div className="absolute top-8 left-8 right-8 bottom-40 bg-gray-200 rounded-[20px]" />
               <div className="absolute bottom-8 left-8 right-8">
                  <h3 className="font-karla text-23 font-bold mb-2">Microplastics in Streams</h3>
                  <p className="font-karla text-20 mb-4">Studying levels of microplastic particles...</p>
                  <Button variant="outline" size="sm">In Progress</Button>
               </div>
            </div>
             {/* Card 2 */}
            <div className="aspect-square bg-gray-50 rounded-[39px] p-8 relative">
               <div className="absolute top-8 left-8 right-8 bottom-40 bg-gray-200 rounded-[20px]" />
               <div className="absolute bottom-8 left-8 right-8">
                  <h3 className="font-karla text-23 font-bold mb-2">Easy DNA Extraction</h3>
                  <p className="font-karla text-20 mb-4">Developing a fast, low-cost method...</p>
                  <Button variant="outline" size="sm">Completed</Button>
               </div>
            </div>
         </div>

         <div className="flex justify-center gap-8">
            <Button className="w-[332px]">Apply</Button>
            <Button className="w-[332px]">Become a Supporter</Button>
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