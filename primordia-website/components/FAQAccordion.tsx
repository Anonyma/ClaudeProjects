'use client';

import React, { useState } from 'react';
import Image from 'next/image';

interface FAQItem {
  question: string;
  answer: string;
}

interface FAQAccordionProps {
  items: FAQItem[];
}

const FAQAccordion: React.FC<FAQAccordionProps> = ({ items }) => {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const toggleItem = (index: number) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  const handleKeyDown = (event: React.KeyboardEvent, index: number) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      toggleItem(index);
    }
  };

  return (
    <div className="space-y-[16px]">
      {items.map((item, index) => {
        const isOpen = openIndex === index;
        const itemId = `faq-item-${index}`;
        const contentId = `faq-content-${index}`;

        return (
          <div key={index} className="relative">
            <button
              id={itemId}
              aria-expanded={isOpen}
              aria-controls={contentId}
              onClick={() => toggleItem(index)}
              onKeyDown={(e) => handleKeyDown(e, index)}
              className="w-full flex items-center justify-between px-[40px] py-[20.5px] bg-white border border-border-light rounded-faq shadow-faq hover:shadow-lg transition-shadow focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-2"
            >
              <span className="font-karla font-normal text-[23px] leading-[1.54] text-black text-left">
                {item.question}
              </span>

              <div
                className={`flex-shrink-0 ml-4 transition-transform ${
                  isOpen ? 'rotate-0' : 'rotate-180'
                }`}
              >
                <Image
                  src="http://localhost:3845/assets/487a73d8c184fd88b96c8045f7b9f67433570f6f.svg"
                  alt=""
                  width={21}
                  height={18}
                  className="w-[21px] h-[18px]"
                />
              </div>
            </button>

            {isOpen && (
              <div
                id={contentId}
                role="region"
                aria-labelledby={itemId}
                className="mt-2 px-[40px] py-[20px] bg-white border border-border-light rounded-faq shadow-faq"
              >
                <p className="font-karla font-normal text-[20px] leading-[1.6] text-black">
                  {item.answer}
                </p>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default FAQAccordion;
