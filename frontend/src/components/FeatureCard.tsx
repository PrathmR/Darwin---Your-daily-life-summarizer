
// import { ReactNode } from 'react';

// interface FeatureCardProps {
//   icon: ReactNode;
//   title: string;
//   description: string;
//   delay: string;
// }

// const FeatureCard = ({ icon, title, description, delay }: FeatureCardProps) => {
//   return (
//     <div className={`bg-arcade-terminal border border-gray-800 rounded-xl p-6 flex flex-col items-center text-center opacity-0 animate-slide-up ${delay}`}>
//       <div className="w-12 h-12 flex items-center justify-center text-arcade-purple mb-4">
//         {icon}
//       </div>
//       <h3 className="text-lg font-semibold mb-2 text-white">{title}</h3>
//       <p className="text-sm text-gray-400">{description}</p>
//     </div>
//   );
// };

// export default FeatureCard;






import { ReactNode } from 'react';

interface FeatureCardProps {
  icon: ReactNode;
  title: string;
  description: string;
  delay: string;
}

const FeatureCard = ({ icon, title, description, delay }: FeatureCardProps) => {
  return (
    <div className={`bg-[#e6f4ef]/90 border border-[#1a8b7e]/20 rounded-lg p-6 flex flex-col items-center text-center opacity-0 animate-slide-up ${delay} shadow-[0_4px_20px_rgba(26,139,126,0.15)] backdrop-blur-sm hover:bg-green-300/50 hover:text-[#e6f4ef] transition-all duration-500 ease-in-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#1a8b7e] focus-visible:ring-offset-2`}>
      <div className="w-12 h-12 flex items-center justify-center bg-[#1a8b7e] text-[#e6f4ef] rounded-lg mb-4 transition-all duration-500 ease-in-out">
        {icon}
      </div>
      <h3 className="text-lg font-medium mb-2 text-[#1a8b7e] hover:text-[#e6f4ef] transition-colors duration-500 ease-in-out">{title}</h3>
      <p className="text-sm text-[#4B5563] tracking-wide transition-colors duration-500 ease-in-out">{description}</p>
    </div>
  );
};

export default FeatureCard;