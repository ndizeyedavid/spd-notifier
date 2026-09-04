import { useState } from "react";
import SplashScreen from "./screens/SplashScreen";
import SampleImage from "@/assets/onboarding/notif.png";
import OnboardingScreen from "./screens/OnboardingScreen";
import AuthScreen from "./screens/AuthScreen";

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<
    "splash" | "onboarding" | "auth" | "main" | "job" | "profile"
  >("auth");
  return (
    <>
      {currentScreen === "splash" && <SplashScreen />}
      {currentScreen === "onboarding" && <OnboardingScreen />}
      {currentScreen === "auth" && <AuthScreen />}
    </>
  );
}
