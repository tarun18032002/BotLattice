import { useEffect, useRef, useState } from "react";
import { loginWithEmail, loginWithGoogleIdToken, registerWithEmail } from "../../api/auth";
import { useStore } from "../../store/useStore";

const AUTH_MODES = {
  login: "login",
  register: "register",
  google: "google",
};

export function AuthPage() {
  const { dispatch } = useStore();
  const googleBtnRef = useRef(null);
  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || "";

  const [mode, setMode] = useState(AUTH_MODES.login);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [loginForm, setLoginForm] = useState({ email: "", password: "" });
  const [registerForm, setRegisterForm] = useState({ name: "", email: "", password: "" });

  const onAuthSuccess = (data) => {
    dispatch({
      type: "SET_AUTH",
      payload: {
        token: data.token,
        user: data.user,
      },
    });
  };

  const submitLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const data = await loginWithEmail(loginForm);
      onAuthSuccess(data);
    } catch (err) {
      setError(err?.message || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  const submitRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const data = await registerWithEmail(registerForm);
      onAuthSuccess(data);
    } catch (err) {
      setError(err?.message || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (mode !== AUTH_MODES.google) return;
    if (!googleClientId) return;

    let active = true;

    const initializeGoogle = () => {
      if (!active) return;
      if (!window.google?.accounts?.id || !googleBtnRef.current) return;

      window.google.accounts.id.initialize({
        client_id: googleClientId,
        callback: async (response) => {
          if (!response?.credential) {
            setError("Google sign-in did not return a token");
            return;
          }

          setLoading(true);
          setError("");
          try {
            const data = await loginWithGoogleIdToken(response.credential);
            onAuthSuccess(data);
          } catch (err) {
            setError(err?.message || "Google login failed");
          } finally {
            setLoading(false);
          }
        },
      });

      googleBtnRef.current.innerHTML = "";
      window.google.accounts.id.renderButton(googleBtnRef.current, {
        type: "standard",
        theme: "outline",
        size: "large",
        shape: "pill",
        text: "continue_with",
        width: 360,
      });
    };

    const scriptId = "google-identity-services";
    const existingScript = document.getElementById(scriptId);
    if (existingScript) {
      initializeGoogle();
    } else {
      const script = document.createElement("script");
      script.id = scriptId;
      script.src = "https://accounts.google.com/gsi/client";
      script.async = true;
      script.defer = true;
      script.onload = initializeGoogle;
      document.head.appendChild(script);
    }

    return () => {
      active = false;
    };
  }, [googleClientId, mode]);

  const googleNotConfigured = !googleClientId;

  const submitGoogleFallback = async (e) => {
    e.preventDefault();
    setError("Google sign-in is not configured. Set VITE_GOOGLE_CLIENT_ID in frontend env.");
  };

  return (
    <div className="min-h-screen bg-[#0b0d11] text-[#e8eaf0] flex items-center justify-center p-4">
      <div className="w-full max-w-xl rounded-2xl border border-[rgba(255,255,255,0.08)] bg-[#111521] p-6 shadow-[0_20px_80px_rgba(0,0,0,0.35)]">
        <div className="mb-5">
          <h1 className="text-[22px] font-semibold">Welcome to BotLattice</h1>
          <p className="text-[12px] text-[#8a93a8] mt-1">Sign in with email/password or Google auth.</p>
        </div>

        <div className="grid grid-cols-3 gap-2 mb-5">
          <button
            className={`rounded-lg px-3 py-2 text-xs border ${mode === AUTH_MODES.login ? "border-[#00e5a0] text-[#00e5a0]" : "border-[rgba(255,255,255,0.12)] text-[#8a93a8]"}`}
            onClick={() => setMode(AUTH_MODES.login)}
          >
            Login
          </button>
          <button
            className={`rounded-lg px-3 py-2 text-xs border ${mode === AUTH_MODES.register ? "border-[#00e5a0] text-[#00e5a0]" : "border-[rgba(255,255,255,0.12)] text-[#8a93a8]"}`}
            onClick={() => setMode(AUTH_MODES.register)}
          >
            Register
          </button>
          <button
            className={`rounded-lg px-3 py-2 text-xs border ${mode === AUTH_MODES.google ? "border-[#00e5a0] text-[#00e5a0]" : "border-[rgba(255,255,255,0.12)] text-[#8a93a8]"}`}
            onClick={() => setMode(AUTH_MODES.google)}
          >
            Google Auth
          </button>
        </div>

        {mode === AUTH_MODES.login && (
          <form className="space-y-3" onSubmit={submitLogin}>
            <input
              className="w-full rounded-lg bg-[#0d1018] border border-[rgba(255,255,255,0.1)] px-3 py-2 text-sm"
              type="email"
              placeholder="Email"
              required
              value={loginForm.email}
              onChange={(e) => setLoginForm((s) => ({ ...s, email: e.target.value }))}
            />
            <input
              className="w-full rounded-lg bg-[#0d1018] border border-[rgba(255,255,255,0.1)] px-3 py-2 text-sm"
              type="password"
              placeholder="Password"
              required
              value={loginForm.password}
              onChange={(e) => setLoginForm((s) => ({ ...s, password: e.target.value }))}
            />
            <button disabled={loading} className="w-full rounded-lg bg-[#00e5a0] text-[#09130f] px-4 py-2.5 text-sm font-semibold disabled:opacity-60">
              {loading ? "Signing in..." : "Sign in"}
            </button>
          </form>
        )}

        {mode === AUTH_MODES.register && (
          <form className="space-y-3" onSubmit={submitRegister}>
            <input
              className="w-full rounded-lg bg-[#0d1018] border border-[rgba(255,255,255,0.1)] px-3 py-2 text-sm"
              type="text"
              placeholder="Name"
              required
              value={registerForm.name}
              onChange={(e) => setRegisterForm((s) => ({ ...s, name: e.target.value }))}
            />
            <input
              className="w-full rounded-lg bg-[#0d1018] border border-[rgba(255,255,255,0.1)] px-3 py-2 text-sm"
              type="email"
              placeholder="Email"
              required
              value={registerForm.email}
              onChange={(e) => setRegisterForm((s) => ({ ...s, email: e.target.value }))}
            />
            <input
              className="w-full rounded-lg bg-[#0d1018] border border-[rgba(255,255,255,0.1)] px-3 py-2 text-sm"
              type="password"
              placeholder="Password"
              required
              value={registerForm.password}
              onChange={(e) => setRegisterForm((s) => ({ ...s, password: e.target.value }))}
            />
            <button disabled={loading} className="w-full rounded-lg bg-[#00e5a0] text-[#09130f] px-4 py-2.5 text-sm font-semibold disabled:opacity-60">
              {loading ? "Creating account..." : "Create account"}
            </button>
          </form>
        )}

        {mode === AUTH_MODES.google && (
          <form className="space-y-3" onSubmit={submitGoogleFallback}>
            {googleNotConfigured ? (
              <div className="rounded-lg border border-[rgba(255,255,255,0.12)] bg-[#0d1018] p-3 text-xs text-[#c8cfdd]">
                Google auth not configured. Add VITE_GOOGLE_CLIENT_ID to frontend env.
              </div>
            ) : (
              <div className="rounded-lg border border-[rgba(255,255,255,0.12)] bg-[#0d1018] p-3 flex items-center justify-center min-h-[74px]">
                <div ref={googleBtnRef} />
              </div>
            )}
            <p className="text-[11px] text-[#8a93a8]">Google popup will return a signed ID token and backend verifies it before creating session.</p>
          </form>
        )}

        {error && <p className="text-[#ff6d7d] text-xs mt-4">{error}</p>}
      </div>
    </div>
  );
}
