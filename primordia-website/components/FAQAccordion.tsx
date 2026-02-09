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
          <div
            key={index}
            className="relative bg-white border border-border-light rounded-faq shadow-faq overflow-hidden transition-all duration-300"
          >
            <button
              id={itemId}
              aria-expanded={isOpen}
              aria-controls={contentId}
              onClick={() => toggleItem(index)}
              onKeyDown={(e) => handleKeyDown(e, index)}
              className="w-full flex items-center justify-between px-[40px] py-[20.5px] hover:bg-gray-50 transition-colors focus:outline-none focus:ring-2 focus:ring-black focus:ring-inset"
            >
              <span className="font-karla font-normal text-[23px] leading-[1.54] text-black text-left">
                {item.question}
              </span>

              <div
                className={`flex-shrink-0 ml-4 transition-transform duration-300 ${
                  isOpen ? 'rotate-0' : 'rotate-180'
                }`}
              >
                <Image
                  src="/assets/487a73d8c184fd88b96c8045f7b9f67433570f6f.svg"
                  alt=""
                  width={21}
                  height={18}
                  className="w-[21px] h-[18px]"
                />
              </div>
            </button>

            <div
              id={contentId}
              role="region"
              aria-labelledby={itemId}
              className={`transition-all duration-300 overflow-hidden ${
                isOpen ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'
              }`}
            >
              <div className="px-[40px] pb-[20px] pt-[8px] border-t border-border-light">
                <p className="font-karla font-normal text-[20px] leading-[1.6] text-black">
                  {item.answer}
                </p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default FAQAccordion;
