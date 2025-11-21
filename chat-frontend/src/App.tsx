import ErrorPopup from "./components/ErrorPopup.tsx";
import { BrowserRouter, Route, Routes } from "react-router";
import { useState } from "react";
import StartPage from "./pages/start-page/StartPage.tsx";
import "./App.module.css";

export default function App() {
  const [showErrorPopup, setShowErrorPopup] = useState(false);
  const [retryAction, setRetryAction] = useState<(() => any) | undefined>(undefined);

  function onError(newRetryAction: () => any) {
    setShowErrorPopup(true);
    setRetryAction(newRetryAction);
  }

  return <BrowserRouter>
    {showErrorPopup
      ? <ErrorPopup
          retryAction={retryAction}
          onClose={() => setShowErrorPopup(false)}/>
      : null}
    <Routes>
      <Route path="/" element={<StartPage onError={onError} />} />
    </Routes>
  </BrowserRouter>;
}