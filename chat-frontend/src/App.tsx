import ErrorPopup from "./components/ErrorPopup.tsx";
import { Route, Routes, useLocation } from "react-router";
import { useState } from "react";
import StartPage from "./pages/start-page/StartPage.tsx";
import { LoginContent } from "./pages/start-page/components/LoginContent.tsx";
import RegisterContent from "./pages/start-page/components/RegisterContent.tsx";
import IndexPage from "./pages/index-page/IndexPage.tsx";
import VerifyEmailPage from "./pages/verify-email-page/VerifyEmailPage.tsx";

export default function App() {
  const location = useLocation();

  const [showErrorPopup, setShowErrorPopup] = useState(false);
  const [retryAction, setRetryAction] = useState<(() => any) | undefined>(undefined);

  function onError(newRetryAction: () => any) {
    setShowErrorPopup(true);
    setRetryAction(newRetryAction);
  }

  return <>
    {showErrorPopup
      ? <ErrorPopup
          retryAction={retryAction}
          onClose={() => setShowErrorPopup(false)}/>
      : null}
    <Routes location={location}>
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
      <Route
        path="/verify-email"
        element={<VerifyEmailPage onError={onError}/>} />
      <Route
        path="/app"
        element={<h1>App page</h1>} />
      </Routes>
  </>;
}