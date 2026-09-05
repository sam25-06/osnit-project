import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "./AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const redirectTo = location.state?.from?.pathname || "/dashboard";
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setFormError(null);
    setIsSubmitting(true);
    try {
      await login(email, password);
      navigate(redirectTo, { replace: true });
    } catch (error) {
      setFormError(error.message || "Authentication failed.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return <main className="login-shell">
    <div className="login-atmosphere"><span className="orbit orbit-one" /><span className="orbit orbit-two" /><span className="grid-glow" /></div>
    <section className="login-brief">
      <div className="brand-lockup login-brand"><div className="brand-mark"><span /></div><div><p className="brand-name">OSNIT</p><p className="brand-caption">Operational intelligence</p></div></div>
      <div className="brief-copy"><p className="eyebrow">Secure access / 07</p><h1>See the signal<br /><i>before it spreads.</i></h1><p>One clear operating picture for the moments that demand precision.</p></div>
      <div className="brief-footer"><span>Classification: internal</span><span>System status <i /></span></div>
    </section>
    <section className="login-card-wrap"><div className="login-card">
      <div className="card-topline"><span>IDENTITY VERIFICATION</span><span>01—02</span></div>
      <div className="login-heading"><h2>Welcome back.</h2><p>Sign in to access your operational workspace.</p></div>
      <form onSubmit={handleSubmit}>
        <label htmlFor="email">Official email <span>Required</span></label>
        <div className="input-shell"><span className="input-prefix">@</span><input id="email" type="email" required autoComplete="username" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="officer@agency.gov" /></div>
        <label htmlFor="password">Passphrase <span>Required</span></label>
        <div className="input-shell"><span className="input-prefix">⌁</span><input id="password" type="password" required autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Enter your passphrase" /></div>
        {formError && <div className="form-error">{formError}</div>}
        <button className="login-submit" type="submit" disabled={isSubmitting}>{isSubmitting ? <><span className="button-spinner" />Verifying identity...</> : <>Enter workspace <span>↗</span></>}</button>
      </form>
      <div className="login-card-footer"><span className="lock-symbol">▣</span><p>Protected by encrypted session controls.<br />Activity is recorded for operational review.</p></div>
    </div><p className="login-help">Need access assistance? <span>Contact your system administrator</span></p></section>
  </main>;
}
