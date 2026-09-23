import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { MiniMartLogo } from '../components/MiniMartLogo';
import { ForgotPasswordModal } from '../components/ForgotPasswordModal';

export const LoginView: React.FC = () => {
  const { users, login, showFlash, sendPasswordResetRequest } = useApp();

  const [selectedUser, setSelectedUser] = useState<number>(users[0]?.id || 1);
  const [email, setEmail] = useState<string>(users[0]?.email || 'admin@pos.local');
  const [password, setPassword] = useState<string>('password');
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [showForgotModal, setShowForgotModal] = useState<boolean>(false);

  const handleSelectUser = (user: (typeof users)[0]) => {
    setSelectedUser(user.id);
    setEmail(user.email);
    setPassword('password');
    setErrorMessage('');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');
    setIsLoading(true);

    setTimeout(() => {
      const success = login(email, password);
      setIsLoading(false);
      if (!success) {
        setErrorMessage('Invalid email or password. Try selecting one of the demo staff profiles below.');
        showFlash('Login failed. Please verify credentials.', 'error');
      } else {
        showFlash('Welcome to Mini Mart POS!', 'success');
      }
    }, 250);
  };

  return (
    <div className="login-wrap">
      <div className="login-card">
        {/* Brand Logo & Header */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: '18px' }}>
          <MiniMartLogo size={96} withRing />
          <h1
            style={{
              margin: '14px 0 4px',
              fontSize: '24px',
              fontWeight: 700,
              color: 'var(--text-dark)',
              letterSpacing: '-0.3px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            Mini Mart
          </h1>
          <p
            className="subtitle"
            style={{
              margin: 0,
              fontSize: '13px',
              color: 'var(--text-muted)'
            }}
          >
            Point-of-Sale &amp; Inventory Management
          </p>
        </div>

        {errorMessage && (
          <div
            className="flash flash-error"
            style={{
              fontSize: '12.5px',
              padding: '10px 12px',
              marginBottom: '16px',
              textAlign: 'left'
            }}
          >
            <span>
              <i className="fa-solid fa-triangle-exclamation" style={{ marginRight: '6px' }}></i>
              {errorMessage}
            </span>
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ textAlign: 'left' }}>
          <div style={{ marginBottom: '14px' }}>
            <label htmlFor="login-email" style={{ display: 'block', marginBottom: '6px', fontSize: '13px', fontWeight: 600 }}>
              Staff Email
            </label>
            <div style={{ position: 'relative' }}>
              <input
                id="login-email"
                type="email"
                required
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="Enter your email"
                style={{
                  width: '100%',
                  padding: '10px 12px 10px 36px',
                  borderRadius: '8px',
                  border: '1px solid var(--border-color)',
                  fontSize: '13.5px',
                  background: 'var(--card-bg)'
                }}
              />
              <i
                className="fa-regular fa-envelope"
                style={{
                  position: 'absolute',
                  left: '12px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: 'var(--text-muted)',
                  fontSize: '14px'
                }}
              ></i>
            </div>
          </div>

          <div style={{ marginBottom: '18px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
              <label htmlFor="login-password" style={{ fontSize: '13px', fontWeight: 600, margin: 0 }}>
                Password / PIN
              </label>
              <button
                type="button"
                onClick={() => setPassword('password')}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'var(--primary)',
                  fontSize: '11.5px',
                  cursor: 'pointer',
                  padding: 0
                }}
              >
                Auto-fill demo password
              </button>
            </div>
            <div style={{ position: 'relative' }}>
              <input
                id="login-password"
                type={showPassword ? 'text' : 'password'}
                required
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="Enter password"
                style={{
                  width: '100%',
                  padding: '10px 38px 10px 36px',
                  borderRadius: '8px',
                  border: '1px solid var(--border-color)',
                  fontSize: '13.5px',
                  background: 'var(--card-bg)'
                }}
              />
              <i
                className="fa-solid fa-lock"
                style={{
                  position: 'absolute',
                  left: '12px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: 'var(--text-muted)',
                  fontSize: '14px'
                }}
              ></i>
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  position: 'absolute',
                  right: '10px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'none',
                  border: 'none',
                  color: 'var(--text-muted)',
                  cursor: 'pointer',
                  padding: '4px'
                }}
                title={showPassword ? 'Hide password' : 'Show password'}
              >
                <i className={`fa-regular ${showPassword ? 'fa-eye-slash' : 'fa-eye'}`}></i>
              </button>
            </div>

            {/* Forgot password link */}
            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '6px' }}>
              <button
                type="button"
                onClick={() => setShowForgotModal(true)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#229ED9',
                  fontSize: '12px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '5px',
                  padding: '2px 0'
                }}
              >
                <i className="fa-solid fa-key" style={{ fontSize: '11px' }}></i>
                Forgot password?
              </button>
            </div>
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={isLoading}
            style={{
              width: '100%',
              padding: '11px',
              fontSize: '14px',
              fontWeight: 600,
              justifyContent: 'center',
              gap: '8px',
              borderRadius: '8px'
            }}
          >
            {isLoading ? (
              <>
                <i className="fa-solid fa-circle-notch fa-spin"></i>
                Signing in...
              </>
            ) : (
              <>
                <i className="fa-solid fa-right-to-bracket"></i>
                Sign In to Mini Mart
              </>
            )}
          </button>
        </form>

        {/* Quick Demo Staff Login */}
        <div style={{ marginTop: '24px', paddingTop: '18px', borderTop: '1px solid var(--border-color)' }}>
          <div
            style={{
              fontSize: '11.5px',
              fontWeight: 600,
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              color: 'var(--text-muted)',
              marginBottom: '10px',
              textAlign: 'center'
            }}
          >
            Or select staff profile to sign in
          </div>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(2, 1fr)',
              gap: '8px'
            }}
          >
            {users.map(user => {
              const isCurrent = selectedUser === user.id;
              const roleDisplay = user.role_name.replace('_', ' ');

              return (
                <button
                  key={user.id}
                  type="button"
                  onClick={() => handleSelectUser(user)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '8px',
                    borderRadius: '8px',
                    border: isCurrent ? '1.5px solid var(--primary)' : '1px solid var(--border-color)',
                    background: isCurrent ? 'rgba(125, 57, 235, 0.08)' : 'var(--bg-color)',
                    cursor: 'pointer',
                    textAlign: 'left',
                    transition: 'all 0.15s ease'
                  }}
                  title={`Sign in as ${user.name} (${roleDisplay})`}
                >
                  <img
                    src={`/uploads/avatars/${user.profile_picture || 'admin.png'}`}
                    alt={user.name}
                    style={{
                      width: '28px',
                      height: '28px',
                      borderRadius: '50%',
                      objectFit: 'cover',
                      border: '1px solid var(--border-color)',
                      flexShrink: 0
                    }}
                    onError={e => {
                      (e.target as HTMLElement).style.display = 'none';
                    }}
                  />
                  <div style={{ minWidth: 0, flex: 1 }}>
                    <div
                      style={{
                        fontSize: '12px',
                        fontWeight: 600,
                        color: 'var(--text-dark)',
                        whiteSpace: 'nowrap',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis'
                      }}
                    >
                      {user.name.split(' ')[0]}
                    </div>
                    <div
                      style={{
                        fontSize: '10.5px',
                        color: 'var(--text-muted)',
                        textTransform: 'capitalize'
                      }}
                    >
                      {roleDisplay}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        <div style={{ marginTop: '16px', textAlign: 'center', fontSize: '11.5px', color: 'var(--text-muted)' }}>
          Powered by Mini Mart POS &bull; Terminal ready
        </div>
      </div>

      <ForgotPasswordModal
        isOpen={showForgotModal}
        onClose={() => setShowForgotModal(false)}
        users={users}
        sendPasswordResetRequest={sendPasswordResetRequest}
        showFlash={showFlash}
        onApplyCredentials={(em, pin) => {
          setEmail(em);
          setPassword(pin);
          const found = users.find(u => u.email === em);
          if (found) setSelectedUser(found.id);
          showFlash('Temporary recovery PIN applied to login form.', 'success');
        }}
      />
    </div>
  );
};

export default LoginView;
