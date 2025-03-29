import React from "react";
import Link from "next/link";

const Hero = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#E0FFFF] via-[#F0F8FF] to-[#E6E6FA]">
      {/* Hero Section */}
      <div className="pt-32 pb-20 px-4 justify-center items-center flex flex-col min-h-screen">
        <div className="max-w-4xl mx-auto text-center justify-center items-center flex flex-col">
          <h1 className="text-5xl md:text-7xl font-bold text-gray-900 mb-8 leading-tight">
            Real-Time Personal Finance Tracker
          </h1>

          <p className="text-xl text-gray-600 mb-12 max-w-3xl mx-auto">
            Track your spending, manage your budget, and achieve your financial
            goals with our intuitive and user-friendly platform.
          </p>
        </div>
      </div>
      <div className="min-h-screen justify-center flex flex-col items-center gap-8">
        <p className="text-3xl md:text-5xl font-bold text-gray-900 mb-8 leading-tight text-center">
          Create or Import your first expenses list today
          <br /> and take control of your finances!
        </p>

        <Link href="/sheet">
          <button className="p-10 cursor-pointer bg-blue-500 text-white rounded-lg hover:bg-blue-600">
            Get started Now
          </button>
        </Link>
      </div>
    </div>
  );
};

export default Hero;
