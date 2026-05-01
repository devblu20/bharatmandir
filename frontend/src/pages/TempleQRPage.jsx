import { useState, useEffect, useRef } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { QRCodeSVG } from 'qrcode.react';
import { MapPin, ArrowLeft, Download, ExternalLink } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { templeAPI } from '../services/api';
import { useTranslatedTemple } from '../hooks/useTranslatedData';

export default function TempleQRPage() {
  const { slug }  = useParams();
  const navigate  = useNavigate();
  const qrRef     = useRef(null);
  const { t }     = useTranslation();

  const [temple,  setTemple]  = useState(null);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState(null);

  // ── Translation hook ──
  const { translated: displayTemple, translating } = useTranslatedTemple(temple);

  useEffect(() => {
    if (!slug || slug === 'undefined') { navigate('/'); return; }
    templeAPI.getBySlug(slug)
      .then(res => setTemple(res.data))
      .catch(() => setError(t('detail.not_found_msg')))
      .finally(() => setLoading(false));
    window.scrollTo(0, 0);
  }, [slug, navigate]);

  const handlePrint = () => window.print();

  const handleDownload = () => {
    const svg = qrRef.current?.querySelector('svg');
    if (!svg) return;
    const canvas  = document.createElement('canvas');
    const size    = 400;
    canvas.width  = canvas.height = size;
    const ctx     = canvas.getContext('2d');
    ctx.fillStyle = '#FFFFFF';
    ctx.fillRect(0, 0, size, size);
    const svgData = new XMLSerializer().serializeToString(svg);
    const img     = new Image();
    img.onload    = () => {
      ctx.drawImage(img, 0, 0, size, size);
      const link    = document.createElement('a');
      link.download = `${slug}-qr-code.png`;
      link.href     = canvas.toDataURL('image/png');
      link.click();
    };
    img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgData)));
  };

  const qrUrl    = `${window.location.origin}/temple/${slug}`;
  const templeId = displayTemple
    ? `BM-${(displayTemple.state||'IN').substring(0,2).toUpperCase()}-${String(displayTemple.id).padStart(4,'0')}`
    : '';

  if (loading) return (
    <div className="qr-page">
      <div className="loading-wrap">
        <div className="spinner" />
        <span className="loading-text">{t('qr.loading')}</span>
      </div>
    </div>
  );

  if (error || !displayTemple) return (
    <div className="qr-page">
      <div className="error-wrap">
        <div className="error-icon">🛕</div>
        <div className="error-title">{t('detail.not_found')}</div>
        <button className="btn-primary" onClick={() => navigate('/')} style={{ marginTop: 16 }}>
          {t('qr.back_home')}
        </button>
      </div>
    </div>
  );

  return (
    <div className="qr-page">
      <style>{`
        @media print {
          body * { visibility: hidden; }
          .qr-full-card, .qr-full-card * { visibility: visible; }
          .qr-full-card { position: fixed; top: 50%; left: 50%; transform: translate(-50%,-50%); box-shadow: none !important; }
          .no-print { display: none !important; }
        }
      `}</style>

      <div className="qr-full-card">

        <div className="no-print" style={{ marginBottom: 20 }}>
          <button onClick={() => navigate(`/temple/${slug}`)} style={{ display: 'flex', alignItems: 'center', gap: 6, background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-light)', fontFamily: 'var(--font-display)', fontSize: 13, letterSpacing: '.04em' }}>
            <ArrowLeft size={14} /> {t('qr.back_to_temple')}
          </button>
        </div>

        {/* Translating indicator */}
        {translating && (
          <div style={{ textAlign: 'center', color: 'var(--saffron)', fontSize: 13, fontFamily: 'var(--font-hindi)', marginBottom: 12 }}>
            ⏳ अनुवाद हो रहा है...
          </div>
        )}

        <span className="qr-full-om">🛕</span>
        <div className="qr-full-platform">{t('qr.platform')}</div>

        <h1 className="qr-full-name">{displayTemple.name}</h1>
        {displayTemple.name_hindi && <div className="qr-full-hindi">{displayTemple.name_hindi}</div>}
        <div className="qr-full-loc">
          <MapPin size={13} />
          {displayTemple.city}, {displayTemple.state}
          {displayTemple.primary_deity && ` · ${displayTemple.primary_deity}`}
        </div>

        {(displayTemple.is_jyotirlinga || displayTemple.is_shaktipeeth) && (
          <div style={{ marginBottom: 16, display: 'flex', gap: 8, justifyContent: 'center', flexWrap: 'wrap' }}>
            {displayTemple.is_jyotirlinga && (
              <span style={{ background: 'linear-gradient(135deg,#B84D00,#C8960C)', color: 'white', padding: '4px 14px', borderRadius: 50, fontSize: 11, fontFamily: 'var(--font-display)', letterSpacing: '.07em' }}>
                ⚡ {t('qr.one_of_12')}
              </span>
            )}
            {displayTemple.is_shaktipeeth && (
              <span style={{ background: 'linear-gradient(135deg,#9B1C1C,#C8960C)', color: 'white', padding: '4px 14px', borderRadius: 50, fontSize: 11, fontFamily: 'var(--font-display)', letterSpacing: '.07em' }}>
                🌸 {t('qr.one_of_51')}
              </span>
            )}
          </div>
        )}

        <hr className="qr-full-divider" />

        <div ref={qrRef} className="qr-full-code">
          <QRCodeSVG value={qrUrl} size={200} fgColor="#3D1F00" bgColor="#FFFFFF" level="H" />
        </div>
        <div className="qr-full-id">{templeId}</div>
        <p className="qr-full-tip">{t('qr.scan_tip')}</p>
        <hr className="qr-full-divider" />

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 24, textAlign: 'left' }}>
          {displayTemple.opening_time && (
            <InfoBox label={t('detail.timing')} value={`${displayTemple.opening_time} – ${displayTemple.closing_time}`} />
          )}
          {displayTemple.entry_fee !== null && (
            <InfoBox label={t('detail.entry_fee')} value={displayTemple.entry_fee === 0 ? t('qr.free_entry') : `₹${displayTemple.entry_fee}`} />
          )}
          {displayTemple.nearest_railway && (
            <InfoBox label={t('detail.nearest_railway')} value={displayTemple.nearest_railway} full />
          )}
        </div>

        <div className="qr-full-actions no-print">
          <button className="btn-primary" onClick={handleDownload}><Download size={14} /> {t('qr.download')}</button>
          <button className="btn-outline" onClick={handlePrint}>🖨️ {t('qr.print')}</button>
          <Link to={`/temple/${slug}`} className="btn-outline"><ExternalLink size={13} /> {t('qr.view_temple')}</Link>
        </div>

      </div>
    </div>
  );
}

function InfoBox({ label, value, full }) {
  return (
    <div style={{ background: 'var(--cream)', borderRadius: 10, padding: '10px 12px', border: '1px solid var(--cream-dark)', gridColumn: full ? '1/-1' : undefined }}>
      <div style={{ fontFamily: 'var(--font-display)', fontSize: 9, letterSpacing: '.1em', color: 'var(--text-light)', marginBottom: 3, textTransform: 'uppercase' }}>{label}</div>
      <div style={{ fontWeight: 700, fontSize: 13, color: 'var(--brown)' }}>{value}</div>
    </div>
  );
}