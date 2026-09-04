import SplashImage from "@/assets/splash-lower.png";
import { FaArrowRightLong } from "react-icons/fa6";

export default function SplashScreen() {
  return (
    <main className="pt-10">
      <h1 className="text-3xl font-semibold text-center px-3">
        Your search for the next opportunity is now simplified!
      </h1>
      <div className="flex flex-col items-center justify-center mt-5">
        <button className="btn btn-primary btn-block btn-circle w-[80%] btn-lg">
          Get Started <FaArrowRightLong className="ml-1" />
        </button>
      </div>
      <img
        src={SplashImage}
        alt="Description"
        className="mx-auto mt-5 h-[470px] w-full object-cover"
      />
    </main>
  );
}
