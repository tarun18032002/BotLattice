import { useStore }          from "./store/useStore";
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
  const { state } = useStore();
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
