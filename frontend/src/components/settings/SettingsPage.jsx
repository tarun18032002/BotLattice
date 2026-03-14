import { useStore }            from "../../store/useStore";
import { Topbar }              from "../layout/Topbar";
import { LLMSettings }         from "./LLMSettings";
import { RetrievalSettings }   from "./RetrievalSettings";
import { SystemPromptEditor }  from "./SystemPromptEditor";

export function SettingsPage() {
  const { state, dispatch } = useStore();
  const { settings } = state;

  const updateSettings = (patch) =>
    dispatch({ type: "UPDATE_SETTINGS", payload: patch });

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <Topbar
        title="Settings"
        subtitle="LLM · Retrieval · Prompts"
      />

      <div className="flex-1 overflow-y-auto p-5 space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <LLMSettings
            settings={settings}
            onChange={updateSettings}
          />
          <RetrievalSettings
            settings={settings}
            onChange={updateSettings}
          />
        </div>

        <SystemPromptEditor
          value={settings.systemPrompt}
          onChange={(v) => updateSettings({ systemPrompt: v })}
        />
      </div>
    </div>
  );
}
