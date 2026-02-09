import React from 'react';
import Button from './Button';

interface ProjectCardProps {
  title: string;
  description: string;
  location: string;
  status: 'In Progress' | 'Completed';
  imageUrl: string;
}

const ProjectCard: React.FC<ProjectCardProps> = ({
  title,
  description,
  location,
  status,
  imageUrl,
}) => {
  return (
    <div className="relative w-[499px] h-[499px] rounded-card overflow-hidden shadow-card">
      {/* Card Background with Gradient */}
      <div className="absolute inset-0">
        <img
          src="/assets/b19a591256bc5de634d2547a52cfb3c58c3b47d0.png"
          alt=""
          className="w-full h-full object-cover opacity-80"
        />
      </div>

      {/* Header Section with White Background */}
      <div className="absolute top-0 left-0 right-0 h-[217px] bg-white rounded-t-card" />

      {/* Content */}
      <div className="relative px-[34px] pt-[249px]">
        <div className="space-y-4">
          <h3 className="font-montserrat font-semibold text-[31px] leading-none text-black">
            {title}
          </h3>
          <p className="font-karla font-normal text-[23px] leading-none text-black">
            {description}
          </p>
          <p className="font-karla font-normal text-[23px] leading-none text-black">
            {location}
          </p>
        </div>

        <div className="mt-[26px]">
          <Button variant="status" size="sm">
            {status}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ProjectCard;
