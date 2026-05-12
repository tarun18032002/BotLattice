import { useEffect, useState } from "react";
import { fetchCurrentUser, logout } from "./api/auth";
import { useStore }          from "./store/useStore";
import { AuthPage }          from "./components/auth/AuthPage";
import { Sidebar }           from "./components/layout/Sidebar";
import { IngestionPage }     from "./components/ingestion/IngestionPage";
import { ChatPage }          from "./components/chat/ChatPage";
import { CollectionsPage }   from "./components/collections/CollectionsPage";
import { SettingsPage }      from "./components/settings/SettingsPage";

const PAGES = {
  ingest:      IngestionPage,
  chat:        ChatPage,
  collections: CollectionsPage,
  settings:    SettingsPage,
};

export default function App() {
  const { state, dispatch } = useStore();
  const [authChecking, setAuthChecking] = useState(true);

  useEffect(() => {
    let active = true;

    (async () => {
      if (!state.auth.token) {
        if (active) setAuthChecking(false);
        return;
      }

      try {
        const data = await fetchCurrentUser(state.auth.token);
        if (!active) return;
        dispatch({
          type: "SET_AUTH",
          payload: {
            token: state.auth.token,
            user: data.user,
          },
        });
      } catch {
        try {
          await logout(state.auth.token);
        } catch {
          // Ignore logout errors during cleanup.
        }
        if (!active) return;
        dispatch({ type: "CLEAR_AUTH" });
      } finally {
        if (active) setAuthChecking(false);
      }
    })();

    return () => {
      active = false;
    };
  }, [dispatch, state.auth.token]);

  if (authChecking) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-[#0b0d11] text-[#e8eaf0]">
        <div className="text-sm text-[#8a93a8]">Checking session...</div>
      </div>
    );
  }

  if (!state.auth.isAuthenticated) {
    return <AuthPage />;
  }

  const ActivePage = PAGES[state.page] ?? IngestionPage;

  return (
    <div className="flex h-screen overflow-hidden bg-[#0b0d11]">
      <Sidebar />
      <main className="flex-1 overflow-hidden flex flex-col">
        <ActivePage />
      </main>
    </div>
  );
}
