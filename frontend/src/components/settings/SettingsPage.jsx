import { useCallback, useEffect, useState } from "react";
import { useStore }            from "../../store/useStore";
import { Topbar }              from "../layout/Topbar";
import { LLMSettings }         from "./LLMSettings";
import { RetrievalSettings }   from "./RetrievalSettings";
import { SystemPromptEditor }  from "./SystemPromptEditor";
import { Button }              from "../ui/Primitives";
import { fetchCurrentSettings, fetchSettingsOptions, saveSettings } from "../../api/settings";

export function SettingsPage() {
  const { state, dispatch } = useStore();
  const { settings } = state;
  const [saving, setSaving] = useState(false);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(true);
  const [llmProviderMeta, setLlmProviderMeta] = useState(null);

  const updateSettings = (patch) =>
    dispatch({ type: "UPDATE_SETTINGS", payload: patch });

  useEffect(() => {
    (async () => {
      try {
        const [serverSettings, serverOptions] = await Promise.all([
          fetchCurrentSettings(),
          fetchSettingsOptions(),
        ]);

        if (serverOptions?.llm_providers && typeof serverOptions.llm_providers === "object") {
          setLlmProviderMeta(serverOptions.llm_providers);
        }

        dispatch({ type: "UPDATE_SETTINGS", payload: serverSettings });
      } catch (err) {
        setStatus(err?.message || "Failed to load settings");
      } finally {
        setLoading(false);
      }
    })();
  }, [dispatch]);

  const onSave = useCallback(async () => {
    setSaving(true);
    setStatus("");
    try {
      const data = await saveSettings(settings);
      dispatch({ type: "UPDATE_SETTINGS", payload: data.settings ?? {} });
      setStatus("Saved");
    } catch (err) {
      setStatus(err?.message || "Failed to save settings");
    } finally {
      setSaving(false);
    }
  }, [settings, dispatch]);

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <Topbar
        title="Settings"
        subtitle="LLM · Retrieval · Prompts"
        actions={(
          <div className="flex items-center gap-2">
            {status && <span className="text-[11px] text-[#8892a4]">{status}</span>}
            <Button
              size="xs"
              variant="outline"
              onClick={onSave}
              disabled={saving || loading}
            >
              {saving ? "Saving..." : "Save"}
            </Button>
          </div>
        )}
      />

      <div className="flex-1 overflow-y-auto p-5 space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <LLMSettings
            settings={settings}
            onChange={updateSettings}
            providerMeta={llmProviderMeta}
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
