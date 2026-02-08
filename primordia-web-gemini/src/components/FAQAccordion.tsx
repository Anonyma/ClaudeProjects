"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";

interface FAQItemProps {
  question: string;
  answer: string;
}

function FAQItem({ question, answer }: FAQItemProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="border-b border-black/10 last:border-0">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between py-6 text-left group"
      >
        <span className="font-karla font-normal text-23 leading-[1.54] pr-8">
          {question}
        </span>
        <div
          className={cn(
            "transform transition-transform duration-200",
            isOpen ? "rotate-90" : "rotate-0"
          )}
        >
          {/* Polygon 1 - Triangle arrow */}
          <svg
            width="21"
            height="18"
            viewBox="0 0 21 18"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className="fill-black"
          >
             <path d="M10.5 18L0.107696 0.75L20.8923 0.75L10.5 18Z" />
          </svg>
        </div>
      </button>
      <div
        className={cn(
          "overflow-hidden transition-all duration-300 ease-in-out font-karla text-20 leading-relaxed opacity-80",
          isOpen ? "max-h-[500px] pb-6" : "max-h-0"
        )}
      >
        {answer}
      </div>
    </div>
  );
}

const faqs = [
  {
    question: "Who can apply to Primordia?",
    answer: "Individuals or teams with a concrete biology experiment idea that can be performed in a community lab or compliant space.",
  },
  {
    question: "Do I need to be part of a community lab to apply?",
    answer: "It is highly recommended as we partner with labs to ensure safety and equipment access, but we can help match you to one.",
  },
  {
    question: "What can grant funds be used for?",
    answer: "Reagents, consumables, small equipment, and lab membership fees.",
  },
  {
    question: "How large are the microgrants?",
    answer: "Typically up to $3000 per project, designed for small proof-of-concept experiments.",
  },
  {
    question: "How long are projects expected to run?",
    answer: "Projects are generally expected to complete their initial experiment within 3-4 months.",
  },
  {
    question: "Can donors remain anonymous?",
    answer: "Yes, donors can choose to remain anonymous on our public pages.",
  },
  {
    question: "How is safety and legal compliance handled in different countries?",
    answer: "We work with local community labs that adhere to their respective national safety and biosafety regulations.",
  },
];

export function FAQAccordion() {
  return (
    <div className="w-full max-w-[1254px] mx-auto bg-white rounded-[39px] border-[2.5px] border-black p-8 md:p-12">
      {faqs.map((faq, index) => (
        <FAQItem key={index} {...faq} />
      ))}
    </div>
  );
}
