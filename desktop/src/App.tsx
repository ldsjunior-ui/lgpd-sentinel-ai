import { useState } from "react";
import MatrixRain from "./components/MatrixRain";
import Sidebar from "./components/Sidebar";
import SetupWizard from "./components/SetupWizard";
import DataMapping from "./components/tabs/DataMapping";
import DPIA from "./components/tabs/DPIA";
import DSR from "./components/tabs/DSR";
import History from "./components/tabs/History";
import AboutLGPD from "./components/tabs/AboutLGPD";
import "./styles.css";

function App() {
  const [setupComplete, setSetupComplete] = useState(
    () => localStorage.getItem("lgpd_setup_complete") === "true"
  );
  const [currentTab, setCurrentTab] = useState("mapping");

  if (!setupComplete) {
    return <SetupWizard onComplete={() => setSetupComplete(true)} />;
  }

  function renderTab() {
    switch (currentTab) {
      case "mapping":
        return <DataMapping />;
      case "dpia":
        return <DPIA />;
      case "dsr":
        return <DSR />;
      case "history":
        return <History />;
      case "about":
        return <AboutLGPD />;
      default:
        return <DataMapping />;
    }
  }

  return (
    <div className="h-screen w-screen flex overflow-hidden bg-[#0d1117]">
      <MatrixRain />
      <Sidebar currentTab={currentTab} onTabChange={setCurrentTab} />
      <main className="flex-1 overflow-y-auto relative z-10">
        <div className="max-w-4xl mx-auto p-6">{renderTab()}</div>
      </main>
    </div>
  );
}

export default App;
