import SampleImage from "@/assets/onboarding/pana.png";
import { FaUser } from "react-icons/fa";
import { IoMdArrowBack } from "react-icons/io";

export default function AuthScreen() {
  return (
    <main className="pt-10 w-[430px]">
      <div className="mb-5 px-4">
        <button className="cursor-pointer">
          <IoMdArrowBack size={24} className="opacity-85" />
        </button>
      </div>
      <div className="flex items-center justify-center relative">
        <img
          src={SampleImage}
          alt="Sample onboarding image"
          className="w-[250px] object-cover relative"
        />
      </div>

      <div className="flex items-center justify-center flex-col mt-[35px] gap-5 px-10">
        <h3 className="text-[16px]">How would you like us to call you?</h3>
        <label className="input">
          <FaUser className="h-[1em] opacity-50" />

          <input type="text" className="grow" placeholder="e.g: Mellow" />
        </label>
        <button className="btn btn-primary btn-block btn-circle mt-4 mb-13">
          Continue
        </button>
      </div>
    </main>
  );
}
