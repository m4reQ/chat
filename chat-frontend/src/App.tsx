import ErrorPopup from "./components/ErrorPopup.tsx";
import { BrowserRouter, Route, Routes } from "react-router";
import { useState } from "react";
import StartPage from "./pages/start-page/StartPage.tsx";
import "./App.module.css";
import { LoginContent } from "./pages/start-page/components/LoginContent.tsx";
import RegisterContent from "./pages/start-page/components/RegisterContent.tsx";
import IndexPage from "./pages/index-page/IndexPage.tsx";

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
      <Route
        index
        element={<IndexPage />} />
      <Route
        path="/login"
        element={
          <StartPage
            content={{
              headerText: "Welcome Back",
              subHeaderText: "Hello, please enter your login details",
              mainElement: <LoginContent onError={onError} />}} />} />
      <Route
        path="/register"
        element={
          <StartPage
            content={{
              headerText: "Create account",
              subHeaderText: "Hi, please enter details for Your new account",
              mainElement: <RegisterContent onError={onError} />}} />} />
    </Routes>
  </BrowserRouter>;
}