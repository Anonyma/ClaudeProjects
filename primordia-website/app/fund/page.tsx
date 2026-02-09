import React from 'react';
import MenuBar from '@/components/MenuBar';
import Footer from '@/components/Footer';
import Button from '@/components/Button';
import StepCard from '@/components/StepCard';
import FAQAccordion from '@/components/FAQAccordion';
import Image from 'next/image';

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

export default function FundExperimentsPage() {
  return (
    <main className="min-h-screen bg-white">
      {/* SECTION - HERO */}
      <section className="relative w-full h-[828px] overflow-hidden">
        <MenuBar />

        <div className="absolute top-[110px] left-1/2 -translate-x-1/2 w-[1262px] h-[698px]">
          {/* Hero Background Image */}
          <div className="absolute left-[10px] top-0 w-[1241px] h-[638px]">
            <img
              src="/assets/39852c721342aaa96278cdc70081f158db4c8611.png"
              alt=""
              className="w-full h-full object-cover"
            />
          </div>

          {/* Title */}
          <h1 className="absolute left-[25px] top-[50px] font-montserrat font-bold text-[80px] leading-none text-black w-[691px]">
            Fund Experiments
          </h1>

          {/* Description */}
          <p className="absolute right-0 top-[309px] font-karla font-normal text-[55px] leading-[1.17] tracking-[-3.85px] text-black text-right w-[793px]">
            Primordia turns your donations into visible experiments and community capacity, not
            overhead and jargon.
          </p>

          {/* CTA Buttons */}
          <div className="absolute left-[448px] top-[557px] flex gap-[25px]">
            <Button variant="secondary" size="md" href="/donate">
              Become a Donor
            </Button>
            <Button variant="primary" size="md" href="/partner">
              Partner on a Themed Round
            </Button>
          </div>

          {/* Payment Logos */}
          <div className="absolute left-[471px] top-[624px] w-[289px] h-[50px]">
            <Image
              src="/assets/a8d195d8b033f652716bf2ab79b3f0c17cde4382.png"
              alt="Payment methods: Visa, Mastercard, Apple Pay"
              width={289}
              height={50}
              className="w-full h-full object-contain"
            />
          </div>
        </div>
      </section>

      {/* SECTION - FOR DONORS */}
      <section className="relative w-full h-[1161px]">
        {/* Background */}
        <div className="absolute left-[40px] top-[47px] w-[1360px] h-[881px] rounded-card opacity-80 overflow-hidden">
          <img
            src="/assets/8d73f6d3cc79c4f4218df42cafdf8d31d713b7f9.png"
            alt=""
            className="w-[112.99%] h-[108.96%] object-cover"
            style={{ left: '-2.04%', top: '-4.2%' }}
          />
        </div>

        <div className="absolute top-[74px] left-1/2 -translate-x-1/2 w-[1294px] h-[1034px]">
          {/* Title */}
          <h2 className="absolute top-[51px] left-[647px] font-montserrat font-bold text-[78px] leading-none text-black text-center">
            For Donors & Partners
          </h2>

          {/* Subtitle */}
          <p className="absolute top-[150px] left-1/2 -translate-x-1/2 font-karla font-normal text-[30px] leading-[1.07] text-black text-center w-[911px]">
            Pool your contribution with others to support concrete biology experiments in community
            labs.
          </p>

          {/* 4 Steps */}
          <div className="absolute left-[16px] top-[255px] flex gap-[31px]">
            <StepCard
              number=""
              title=""
              description="Pooled donations fund small experiments that would never fit traditional grants."
              iconUrl=""
              variant="donors"
            />
            <StepCard
              number=""
              title=""
              description="Transparent reporting through public lab notes, summaries, and showcases."
              iconUrl=""
              variant="donors"
            />
            <StepCard
              number=""
              title=""
              description="Minimal overhead of 5% to support digital service fees."
              iconUrl=""
              variant="donors"
            />
            <StepCard
              number=""
              title=""
              description="Option for institutions to provide matching pools that are allocated via community voting or quadratic funding."
              iconUrl=""
              variant="donors"
            />
          </div>

          {/* Donations Graphic */}
          <div className="absolute left-[161px] top-[624px] w-[992px] h-[400px]">
            {/* DONATIONS Title */}
            <h3 className="absolute top-0 left-1/2 -translate-x-1/2 font-montserrat font-semibold text-[36px] leading-none text-black text-center">
              DONATIONS
            </h3>

            {/* Arrow Vector */}
            <div className="absolute left-[148px] top-[57px] w-[696px] h-[57px]">
              <Image
                src="/assets/54d8cd4a62e3b957bb65c8f803bb503852acc155.svg"
                alt=""
                width={696}
                height={57}
                className="w-full h-auto"
              />
            </div>

            {/* Three Circles with Icons */}
            <div className="absolute top-[106px] left-0 flex justify-between w-full">
              {/* Experiment Grants */}
              <div className="flex flex-col items-center">
                <div className="relative w-[218px] h-[218px]">
                  <Image
                    src="/assets/e7e0d4ed436a8a6b39bdbeef41060633bee97592.svg"
                    alt=""
                    width={218}
                    height={218}
                  />
                  <div className="absolute top-[-4px] left-1/2 -translate-x-1/2 w-[151px] h-[185px]">
                    <Image
                      src="/assets/f39ae31b7771689f3c1fa20426744bd06f34552e.png"
                      alt="Pipette icon"
                      width={151}
                      height={185}
                      className="w-full h-full object-contain"
                    />
                  </div>
                </div>
                <p className="mt-6 font-karla font-medium text-[28px] leading-[1.07] text-black text-center w-[296px]">
                  Experiment Grants
                </p>
              </div>

              {/* Lab Access */}
              <div className="flex flex-col items-center">
                <div className="relative w-[218px] h-[218px]">
                  <Image
                    src="/assets/e7e0d4ed436a8a6b39bdbeef41060633bee97592.svg"
                    alt=""
                    width={218}
                    height={218}
                  />
                  <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[126px] h-[204px]">
                    <Image
                      src="/assets/3b21be1039f6340027e437d94df81f738eec80ca.png"
                      alt="Microscope icon"
                      width={126}
                      height={204}
                      className="w-full h-full object-contain"
                    />
                  </div>
                </div>
                <p className="mt-6 font-karla font-medium text-[28px] leading-[1.07] text-black text-center w-[296px]">
                  Lab Access
                </p>
              </div>

              {/* Support Small Program Operations */}
              <div className="flex flex-col items-center">
                <div className="relative w-[218px] h-[218px]">
                  <Image
                    src="/assets/e7e0d4ed436a8a6b39bdbeef41060633bee97592.svg"
                    alt=""
                    width={218}
                    height={218}
                  />
                  <div className="absolute top-[66px] left-1/2 -translate-x-1/2 w-[142px] h-[106px]">
                    <Image
                      src="/assets/b29f79ab71bd00aa97f1db350e76a7ffe51b3907.png"
                      alt="Coins icon"
                      width={142}
                      height={106}
                      className="w-full h-full object-contain"
                    />
                  </div>
                </div>
                <p className="mt-6 font-karla font-medium text-[28px] leading-[1.07] text-black text-center w-[296px]">
                  Support Small Program Operations
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION - FAQs */}
      <section className="relative w-full h-[780px]">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[1440px] h-[740px]">
          {/* Background - Tall enough for all expanded FAQ items */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[1254px] h-[700px] rounded-section opacity-80 overflow-hidden">
            <img
              src="/assets/e42062b9935acba3ba062eb6a431490b57cca7e0.png"
              alt=""
              className="w-full h-full object-cover"
            />
          </div>

          {/* Title */}
          <h2 className="absolute left-[175px] top-[69px] font-montserrat font-bold text-[32px] leading-[1.54] text-black">
            FAQs
          </h2>

          {/* FAQ Items */}
          <div className="absolute left-[291px] top-[54px] w-[922px]">
            <FAQAccordion items={faqData} />
          </div>
        </div>
      </section>

      {/* SECTION - FOOTER */}
      <Footer />
    </main>
  );
}
