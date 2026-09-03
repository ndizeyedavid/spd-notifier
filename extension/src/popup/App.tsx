import { useState } from "react";
import SplashScreen from "./components/SplashScreen";

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<
    "splash" | "onboarding" | "main" | "job" | "profile"
  >("splash");
  return (
    <>
      {/* {currentScreen === "splash" && <SplashScreen />} */}
      <main className="pt-10">Onboardingi</main>
    </>
  );
}
