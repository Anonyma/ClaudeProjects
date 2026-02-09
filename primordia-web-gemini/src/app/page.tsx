import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { Section } from "@/components/Section";
import { Button } from "@/components/Button";
import { FAQAccordion } from "@/components/FAQAccordion";

export default function Home() {
  return (
    <main className="min-h-screen bg-white">
      {/* NAVBAR + HERO = 828px in Figma */}
      <div className="h-[828px] relative overflow-hidden">
        <Navbar />
        
        {/* HERO Content - Figma Frame 1 is at y=80, height 680 */}
        <div className="absolute top-[80px] left-1/2 -translate-x-1/2 w-[1350px] h-[680px] z-0">
             {/* Background Shape */}
             <div className="absolute left-[63px] top-[22px] w-[1241px] h-[658px] z-0">
                <img src="/images/hero-shape.png" alt="" className="w-full h-full object-cover" />
             </div>

             {/* Content Layer */}
             <div className="relative z-10 h-full w-full">
                <h1 className="absolute top-[34px] left-1/2 -translate-x-1/2 font-futura font-bold text-125 tracking-[-10px] leading-none text-black whitespace-nowrap">
                  PRIMORDIA
                </h1>

                <h2 className="absolute top-[407px] right-[63px] font-karla font-medium text-66 leading-[1.13] tracking-[-4.62px] text-right w-[730px] text-black">
                   Funding Early Biology Experiments in DIY Labs
                </h2>

                <div className="absolute top-[579px] left-[640px] flex gap-[26px]"> 
                   <div className="flex flex-col items-center gap-4 relative">
                      <Button className="w-[294px]">Apply</Button>
                      <span className="font-karla text-18 font-medium opacity-100 text-center whitespace-nowrap absolute top-[68px]">Up-to $3000 for your project</span>
                   </div>
                   <div className="flex flex-col items-center gap-4 relative">
                       <Button variant="primary" className="w-[318px]">Fund Experiments</Button>
                       <span className="font-karla text-18 font-medium opacity-100 text-center whitespace-nowrap absolute top-[68px]">Support with as little as 1$/month</span>
                   </div>
                </div>
             </div>
        </div>
      </div>

      {/* WHAT IS PRIMORDIA - Height 840px */}
      <section className="h-[840px] relative">
         <div className="relative w-full h-[800px] top-[20px]">
             {/* Background Shape */}
             <div className="absolute top-[47px] left-[101px] w-[1237px] h-[717px] z-0">
                 <img src="/images/bg-shape.png" alt="" className="w-full h-full" />
             </div>
             
             {/* Illustration */}
             <div className="absolute top-[310px] left-[134px] w-[586px] h-[362px] z-10 mix-blend-multiply opacity-90">
                 <img src="/images/primordia-illust.png" alt="" className="w-full h-full object-cover" />
             </div>

             {/* Text Content */}
             <div className="relative z-20">
                 <h2 className="absolute top-[57px] left-[190px] font-montserrat font-bold text-78 leading-none">
                    What is<br />Primordia?
                 </h2>
                 <p className="absolute top-[311px] left-[735px] w-[586px] font-karla font-normal text-31 leading-[1.48]">
                    Primordia is a microgrants program for early stage biology experiments run in community labs and other compliant spaces. We help people move ideas out of notebooks and into the lab by providing small, fast grants and a structure for sharing lab notes, results, and stories.
                 </p>
             </div>
         </div>
      </section>

      {/* HOW IT WORKS - Height 906px */}
      <section className="h-[906px] relative px-[60px]">
         <div className="absolute top-[102px] left-[422px]">
            <h2 className="font-montserrat font-bold text-78 leading-none">How it Works</h2>
         </div>
         <div className="absolute top-[211px] left-1/2 -translate-x-1/2 w-[1066px]">
            <p className="font-karla text-31 leading-tight text-center">
               Simple cycles for experiments that fit in months and micro-budgets.
            </p>
         </div>

         {/* Steps Grid - Y=271 in Figma */}
         <div className="absolute top-[271px] left-[62px] right-[62px] grid grid-cols-5 gap-6">
            {[1, 2, 3, 4, 5].map((step) => (
                <div key={step} className="bg-white rounded-[20px] p-6 h-[466px] flex flex-col justify-between border-[2.5px] border-black">
                   <div className="flex flex-col gap-4">
                      <span className="font-montserrat font-bold text-31 block">{step}.</span>
                      <h3 className="font-montserrat font-bold text-20 uppercase tracking-wide leading-tight min-h-[48px]">
                        {step === 1 && "APPLY WITH A CONCRETE EXPERIMENT"}
                        {step === 2 && "REVIEW AND SELECTION"}
                        {step === 3 && "MICROGRANTS AND LAB ACCESS"}
                        {step === 4 && "LAB NOTES AND UPDATES"}
                        {step === 5 && "SHOWCASE AND NEXT STEPS"}
                      </h3>
                      <p className="font-karla text-20 leading-snug">
                        {step === 1 && "Teams propose a focused experiment they can run in a community lab or other compliant space within a few months."}
                        {step === 2 && "Applications are reviewed by a panel of community lab leaders and practitioners."}
                        {step === 3 && "Selected teams receive a flexible microgrant and plug into a local lab."}
                        {step === 4 && "Grantees commit to sharing short updates and lab notes during the grant period."}
                        {step === 5 && "At the end of the cycle, projects share results in a public session and written summary."}
                      </p>
                   </div>
                   <div className="h-[120px] bg-gray-100 rounded-[10px] w-full mt-auto" />
                </div>
            ))}
         </div>
         
         <div className="absolute top-[789px] left-1/2 -translate-x-1/2">
            <Button className="w-[408px]">View Funded Experiments</Button>
         </div>
      </section>

      {/* DEFINITION SECTION - Height 480px */}
      <section className="h-[480px] relative">
          <div className="absolute top-[20px] left-[94px] right-[94px] h-[440px]">
             <div className="absolute inset-0 bg-[#F2F2F2] rounded-[100px] -rotate-1 z-0" />
             <div className="relative z-10 flex items-center justify-center h-full text-center p-20">
                <p className="font-karla text-31 leading-[1.48] max-w-[772px]">
                    In biology, a primordium is an organ or tissue in its earliest stage of development. Primordia is a collection of those beginnings. That is what this initiative exists for: many small, early experiments that can grow into something bigger.
                </p>
             </div>
          </div>
      </section>

      {/* STORIES & LAB NOTES - Height 1467px */}
      <section className="h-[1467px] relative">
         <div className="flex flex-col items-center absolute top-[68px] left-0 right-0">
            <h2 className="font-montserrat font-bold text-78 leading-none mb-4 text-center">Stories & Lab Notes</h2>
            <p className="font-karla text-31 text-center opacity-60">Learn about DIY community bio initiatives</p>
         </div>

         {/* Grid starting at Y=159 within section */}
         <div className="absolute top-[227px] left-1/2 -translate-x-1/2 grid grid-cols-2 gap-[55px]">
            {/* Card 1 */}
            <div className="w-[499px] h-[499px] bg-white border-[2.5px] border-black rounded-[39px] p-8 relative flex flex-col items-center text-center">
               <div className="w-full h-[215px] bg-gray-200 rounded-[20px] mb-8" />
               <h3 className="font-karla text-23 font-bold mb-2">Microplastics in Streams</h3>
               <p className="font-karla text-20 mb-8 max-w-[432px]">Studying levels of microplastic particles in local streams. Open Bio Lab, Boston</p>
               <Button variant="outline" size="sm" className="w-[204px]">In Progress</Button>
            </div>
             {/* Card 2 */}
            <div className="w-[499px] h-[499px] bg-white border-[2.5px] border-black rounded-[39px] p-8 relative flex flex-col items-center text-center">
               <div className="w-full h-[215px] bg-gray-200 rounded-[20px] mb-8" />
               <h3 className="font-karla text-23 font-bold mb-2">Easy DNA Extraction</h3>
               <p className="font-karla text-20 mb-8 max-w-[432px]">Developing a fast, low-cost DNA extraction method. Community Lab, Oakland</p>
               <Button variant="outline" size="sm" className="w-[204px]">Completed</Button>
            </div>
         </div>

         <div className="absolute top-[1290px] left-1/2 -translate-x-1/2 flex gap-8">
            <Button className="w-[332px]">Apply</Button>
            <Button className="w-[332px]">Become a Supporter</Button>
         </div>
      </section>

      {/* FAQs - Height 617px */}
      <section className="h-[617px] relative px-[60px]">
         <div className="absolute top-[69px] left-[175px]">
            <h2 className="font-montserrat font-bold text-78 leading-none">FAQs</h2>
         </div>
         <div className="absolute top-[39px] left-[291px] right-[229px]">
            <FAQAccordion />
         </div>
      </section>

      <Footer />
    </main>
  );
}