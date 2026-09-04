import SampleImage from "@/assets/onboarding/notif.png";
import OnboardingBackground from "@/assets/onboarding/bg.png";
import { FiChevronsRight } from "react-icons/fi";

export default function OnboardingScreen() {
  return (
    <main className="pt-10">
      <div className="flex justify-end mb-[29px] px-6 relative">
        <a
          href="#"
          className="flex items-center justify-center w-fit text-[12px] absolute -top-2 z-10"
        >
          Skip <FiChevronsRight size={17} />
        </a>
      </div>

      <div className="flex items-center justify-center relative">
        <img
          src={OnboardingBackground}
          alt="Onboarding background"
          className="w-[352px] object-cover absolute -top-10"
        />
        <img
          src={SampleImage}
          alt="Sample onboarding image"
          className="w-[250px] object-cover relative"
        />
      </div>

      <div className="flex items-center justify-center flex-col gap-[17px] mt-[45px] px-[40px]">
        <h3 className="text-[18px] font-semibold">Create Your Profile</h3>
        <p className="text-[14px] text-center">
          Complete your profile to help you find job & internship opportunities
          easily!
        </p>
      </div>

      <div className="px-10 mt-[25px] flex flex-col gap-5 mb-5">
        <div className="flex items-center justify-center gap-[5px]">
          {[1, 2, 3].map((_, i) => (
            <div
              key={i}
              className={`size-[5px] ${i == 0 && "w-[25px]"} bg-[#D9D9D9] rounded-full`}
            />
          ))}
        </div>
        <button className="btn btn-info btn-block btn-circle">Next</button>
      </div>
    </main>
  );
}
