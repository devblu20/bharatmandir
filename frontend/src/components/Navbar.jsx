import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Search } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useLang } from '../LangContext';

export default function Navbar() {
  const [query,   setQuery] = useState('');
  const navigate  = useNavigate();
  const location  = useLocation();
  const { t }               = useTranslation();
  const { lang, changeLang } = useLang();

  const handleSearch = (e) => {
    e.preventDefault();
    if (query.trim()) {
      navigate(`/search?q=${encodeURIComponent(query.trim())}`);
      setQuery('');
    }
  };

  const isActive = (path) => location.pathname === path;

  const NAV_LINKS = [
    { to: '/',              label: t('nav.home') },
    { to: '/search',        label: t('nav.search') },
    { to: '/map',           label: t('nav.map') },
    { to: '/route-planner', label: t('nav.route') },
  ];

  const tickerText = '🔱 OM NAMAH SHIVAYA  ·  JAI SHRI RAM  ·  HAR HAR MAHADEV  ·  JAI MATA DI  ·  JAI GANESH  ·  HARE KRISHNA HARE RAM  ·  ';

  return (
    <>
      <div className="ticker-wrap">
        <div className="ticker-track">
          <span className="ticker-content">{tickerText}{tickerText}</span>
        </div>
      </div>

      <nav className="navbar">
        <div className="navbar-inner">

          <Link to="/" className="nav-logo">
            <span className="nav-logo-icon">🛕</span>
            <div>
              <span className="nav-logo-name">BharatMandir</span>
              <span className="nav-logo-sub">{t('nav.logo_sub')}</span>
            </div>
          </Link>

          <form className="nav-search-form" onSubmit={handleSearch}>
            <Search size={16} className="nav-search-icon" />
            <input
              id="nav-search"
              name="nav-search"
              className="nav-search-input"
              type="text"
              placeholder={t('search_placeholder')}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </form>

          <div className="nav-actions" style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            {NAV_LINKS.map(link => (
              <Link
                key={link.to}
                to={link.to}
                style={{
                  padding: '8px 16px',
                  borderRadius: 50,
                  fontFamily: 'var(--font-display)',
                  fontSize: 12,
                  letterSpacing: '.05em',
                  textDecoration: 'none',
                  transition: 'var(--transition)',
                  background: isActive(link.to) ? 'var(--saffron)' : 'transparent',
                  color: isActive(link.to) ? 'white' : 'var(--text-mid)',
                  border: `2px solid ${isActive(link.to) ? 'var(--saffron)' : 'var(--cream-dark)'}`,
                  whiteSpace: 'nowrap',
                }}
              >
                {link.label}
              </Link>
            ))}

            <div style={{ width: 1, height: 24, background: 'var(--cream-dark)', margin: '0 4px' }} />

            <select
              value={lang}
              onChange={(e) => changeLang(e.target.value)}
              style={{
                padding: '7px 28px 7px 12px',
                borderRadius: 50,
                border: '2px solid var(--cream-dark)',
                background: 'white',
                color: 'var(--brown)',
                fontFamily: 'var(--font-display)',
                fontSize: 12,
                fontWeight: 600,
                cursor: 'pointer',
                outline: 'none',
                letterSpacing: '.05em',
                appearance: 'none',
                backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23B84D00' stroke-width='2.5'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E")`,
                backgroundRepeat: 'no-repeat',
                backgroundPosition: 'right 10px center',
              }}
            >
              <option value="en">🌐 English</option>
              <option value="hi">🇮🇳 हिंदी</option>
              <option value="mr">🟠 मराठी</option>
              <option value="ta">🌺 தமிழ்</option>
            </select>
          </div>

        </div>
      </nav>
    </>
  );
}