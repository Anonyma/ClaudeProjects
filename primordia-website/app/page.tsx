import React from 'react';
import MenuBar from '@/components/MenuBar';
import Footer from '@/components/Footer';
import Button from '@/components/Button';
import StepCard from '@/components/StepCard';
import ProjectCard from '@/components/ProjectCard';
import FAQAccordion from '@/components/FAQAccordion';

const faqData = [
  {
    question: 'Who can apply to Primordia?',
    answer:
      'Anyone with a biology experiment idea that can be run in a community lab or compliant space can apply. We welcome researchers, students, hobbyists, and anyone passionate about advancing biology.',
  },
  {
    question: 'Do I need to be part of a community lab to apply?',
    answer:
      'Yes, you need access to a community lab or other compliant laboratory space. We can help connect you with community labs in your area if needed.',
  },
  {
    question: 'What can grant funds be used for?',
    answer:
      'Grants can be used for reagents, consumables, lab membership fees, and other direct experimental costs. Funds cannot be used for salaries or overhead.',
  },
  {
    question: 'How large are the microgrants?',
    answer:
      'Microgrants typically range from $500 to $3,000, depending on the scope of the experiment and available funding in each round.',
  },
  {
    question: 'How long are projects expected to run?',
    answer:
      'Projects should be completable within 2-4 months. We focus on experiments that fit micro-budgets and short timelines.',
  },
  {
    question: 'Can donors remain anonymous?',
    answer:
      'Yes, donors can choose to remain anonymous if they prefer. We respect your privacy preferences.',
  },
  {
    question: 'How is safety and legal compliance handled in different countries?',
    answer:
      'All experiments must be conducted in compliant spaces that follow local regulations and biosafety standards. Community labs are required to maintain proper safety protocols.',
  },
];

export default function Home() {
  return (
    <main className="min-h-screen bg-white">
      {/* SECTION - HERO */}
      <section className="relative w-full h-[828px] overflow-hidden">
        <MenuBar />

        <div className="absolute top-[80px] left-1/2 -translate-x-1/2 w-[1350px] h-[680px]">
          {/* Hero Background Image */}
          <div className="absolute left-[63px] top-[22px] w-[1241px] h-[658px]">
            <img
              src="http://localhost:3845/assets/32461e24d0d9c8497991428510487f8da2c90c15.png"
              alt=""
              className="w-full h-full object-cover"
            />
          </div>

          {/* Logo */}
          <h1 className="absolute left-[64px] top-[34px] font-futura font-bold text-[125px] leading-none tracking-[-10px] text-black text-center w-[739px]">
            PRIMORDIA
          </h1>

          {/* Tagline */}
          <p className="absolute right-[40px] top-[407px] font-karla font-medium text-[66px] leading-[1.13] tracking-[-4.62px] text-black text-right w-[730px]">
            Funding Early Biology Experiments in DIY Labs
          </p>

          {/* CTA Buttons - Span full width under subtitle */}
          <div className="absolute right-[40px] top-[560px] flex gap-[16px] w-[730px] justify-between">
            <div className="relative flex-1">
              <Button variant="secondary" size="md" href="/apply" className="w-full">
                Apply
              </Button>
              <p className="absolute top-[68px] left-1/2 -translate-x-1/2 font-karla font-medium text-[18px] leading-[1.67] text-black text-center w-full whitespace-nowrap">
                Up-to $3000 for your project
              </p>
            </div>

            <div className="relative flex-1">
              <Button variant="primary" size="md" href="/fund" className="w-full">
                Fund Experiments
              </Button>
              <p className="absolute top-[68px] left-1/2 -translate-x-1/2 font-karla font-medium text-[18px] leading-[1.67] text-black text-center w-full whitespace-nowrap">
                Support with as little as 1$/month
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION - WHAT IS PRIMORDIA */}
      <section className="relative w-full h-[840px]">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[1440px] h-[800px]">
          {/* Background Shape with Illustration */}
          <div className="absolute left-[101px] top-[47px] w-[1237px] h-[717px]">
            <img
              src="http://localhost:3845/assets/0b68b04ef484612a8302eacb563e9a74db16e442.png"
              alt=""
              className="w-full h-full object-cover"
            />
          </div>

          <div className="absolute left-[134px] top-[283px] w-[586px] h-[362px] mix-blend-multiply opacity-90">
            <img
              src="http://localhost:3845/assets/77f49b00e2c6d6dbc0ba3c392b5749f9e7ec5c28.png"
              alt=""
              className="w-full h-full object-cover"
            />
          </div>

          {/* Title */}
          <h2 className="absolute left-[190px] top-[57px] font-montserrat font-bold text-[78px] leading-none text-black">
            What is
            <br />
            Primordia?
          </h2>

          {/* Description */}
          <p className="absolute left-[735px] top-[311px] font-karla font-normal text-[31px] leading-[1.48] text-black w-[586px]">
            Primordia is a microgrants program for early stage biology experiments run in community
            labs and other compliant spaces. We help people move ideas out of notebooks and into the
            lab by providing small, fast grants and a structure for sharing lab notes, results, and
            stories.
          </p>
        </div>
      </section>

      {/* SECTION - HOW IT WORKS */}
      <section className="relative w-full h-[950px]">
        <div className="absolute top-[0px] left-1/2 -translate-x-1/2 w-[1440px] h-[950px]">
          {/* Title */}
          <h2 className="absolute top-[70px] left-1/2 -translate-x-1/2 font-montserrat font-bold text-[78px] leading-none text-black text-center">
            How it Works
          </h2>

          {/* Subtitle */}
          <p className="absolute top-[175px] left-1/2 -translate-x-1/2 font-karla font-normal text-[32px] leading-none text-black text-center w-[1066px]">
            Simple cycles for experiments that fit in months and micro-budgets.
          </p>

          {/* Steps */}
          <div className="absolute left-1/2 -translate-x-1/2 top-[250px] flex gap-[42px] w-[1280px] justify-center">
            <StepCard
              number="1."
              title="APPLY WITH A CONCRETE EXPERIMENT"
              description="Teams propose a focused experiment they can run in a community lab or other compliant space within a few months."
              iconUrl="http://localhost:3845/assets/9afca041dba5cd1fa389abbb0765a0042dbe5236.png"
            />
            <StepCard
              number="2."
              title="REVIEW AND SELECTION"
              description="Applications are reviewed by a panel of community lab leaders and practitioners. In some rounds we also use community voting and quadratic matching to allocate part of the pool."
              iconUrl="http://localhost:3845/assets/ea4670ec3d4f8db0d31297273878f93a6c92fe2e.png"
            />
            <StepCard
              number="3."
              title="MICROGRANTS AND LAB ACCESS"
              description="Selected teams receive a flexible microgrant (for reagents, consumables, and a portion for lab membership) and plug into a local lab."
              iconUrl="http://localhost:3845/assets/63923dde393fae74daf3ce68223f2f650045cfcb.png"
            />
            <StepCard
              number="4."
              title="LAB NOTES AND UPDATES"
              description="Grantees commit to sharing short updates and lab notes during the grant period, building an open portfolio of their progress."
              iconUrl="http://localhost:3845/assets/075f86b177a42c4a339421f3181e9fa8f9327235.png"
            />
            <StepCard
              number="5."
              title="SHOWCASE AND NEXT STEPS"
              description="At the end of the cycle, projects share results in a public session and written summary. Some may continue with follow on grants, partnerships, or company formation."
              iconUrl="http://localhost:3845/assets/ff65de78e09e9f9541b2e09040621bf6607e10a5.png"
            />
          </div>

          {/* CTA Button */}
          <div className="absolute left-1/2 -translate-x-1/2 top-[830px]">
            <Button variant="primary" size="lg" href="#stories">
              View Funded Experiments
            </Button>
          </div>
        </div>
      </section>

      {/* SECTION - DEFINITION */}
      <section className="relative w-full h-[520px] mt-[80px]">
        {/* Background Shape */}
        <div className="absolute left-[94px] top-[40px] w-[1262px] h-[440px]">
          <img
            src="http://localhost:3845/assets/440309f25a5c626dc056db5e980b27ab8298fd9d.png"
            alt=""
            className="w-full h-full object-cover"
          />
        </div>

        {/* White Box Container */}
        <div className="absolute top-[140px] left-[240px] w-[780px] h-[300px] bg-white rounded-[50px]" />

        {/* Text */}
        <p className="absolute top-[140px] left-[240px] font-karla font-medium text-[30px] leading-[1.63] text-black w-[740px] z-10 py-8 px-10">
          In biology, a primordium is an organ or tissue in its earliest stage of development.
          Primordia is a collection of those beginnings. That is what this initiative exists for:
          many small, early experiments that can grow into something bigger.
        </p>
      </section>

      {/* SECTION - STORIES */}
      <section id="stories" className="relative w-full h-[1580px] opacity-90 mb-[100px]">
        <div className="absolute left-[120px] top-[68px] w-[1206px] h-[1384px]">
          {/* Title */}
          <h2 className="absolute top-[10px] left-1/2 -translate-x-1/2 font-montserrat font-semibold text-[66px] leading-none text-black text-center whitespace-nowrap">
            Stories & Lab Notes
          </h2>

          {/* Subtitle */}
          <p className="absolute top-[102px] left-1/2 -translate-x-1/2 font-karla font-normal text-[32px] leading-none text-black text-center w-[1066px]">
            Learn about DIY community bio initiatives
          </p>

          {/* Project Cards - Row 1 */}
          <div className="absolute top-[159px] left-[76px] flex gap-[55px]">
            <ProjectCard
              title="Microplastics in Streams"
              description="Studying levels of microplastic particles in local streams."
              location="Open Bio Lab, Boston"
              status="In Progress"
              imageUrl="http://localhost:3845/assets/b19a591256bc5de634d2547a52cfb3c58c3b47d0.png"
            />
            <ProjectCard
              title="Easy DNA Extraction"
              description="Developing a fast, low-cost DNA extraction method."
              location="Community Lab, Oakland"
              status="Completed"
              imageUrl="http://localhost:3845/assets/b19a591256bc5de634d2547a52cfb3c58c3b47d0.png"
            />
          </div>

          {/* Project Cards - Row 2 */}
          <div className="absolute top-[712px] left-[76px] flex gap-[55px]">
            <ProjectCard
              title="Microplastics in Streams"
              description="Studying levels of microplastic particles in local streams."
              location="Open Bio Lab, Boston"
              status="In Progress"
              imageUrl="http://localhost:3845/assets/b19a591256bc5de634d2547a52cfb3c58c3b47d0.png"
            />
            <ProjectCard
              title="Easy DNA Extraction"
              description="Developing a fast, low-cost DNA extraction method."
              location="Community Lab, Oakland"
              status="Completed"
              imageUrl="http://localhost:3845/assets/b19a591256bc5de634d2547a52cfb3c58c3b47d0.png"
            />
          </div>

          {/* CTA Buttons */}
          <div className="absolute bottom-0 left-[259px] flex gap-[23px]">
            <Button variant="secondary" size="md" href="/apply" fixedWidth="332px">
              Apply
            </Button>
            <Button variant="primary" size="md" href="/fund" fixedWidth="332px">
              Become a Supporter
            </Button>
          </div>
        </div>
      </section>

      {/* SECTION - FAQs */}
      <section className="relative w-full h-[980px] mb-[20px]">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[1440px] h-[940px]">
          {/* Background - Tall enough for all expanded FAQ items */}
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1254px] h-[900px] rounded-section opacity-80">
            <img
              src="http://localhost:3845/assets/e42062b9935acba3ba062eb6a431490b57cca7e0.png"
              alt=""
              className="w-full h-full object-cover rounded-section"
            />
          </div>

          {/* Title */}
          <h2 className="absolute left-[175px] top-[50px] font-montserrat font-bold text-[32px] leading-[1.54] text-black z-10">
            FAQs
          </h2>

          {/* FAQ Items Container */}
          <div className="absolute left-[291px] top-[54px] w-[922px] z-10">
            <FAQAccordion items={faqData} />
          </div>
        </div>
      </section>

      {/* SECTION - FOOTER */}
      <Footer />
    </main>
  );
}
