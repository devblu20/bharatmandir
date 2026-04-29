import { useState, useEffect } from 'react';
import { useLang } from '../LangContext';
import { translateTemples, translateTemple } from '../services/translate';

// Hook for a list of temples
export function useTranslatedTemples(temples) {
  const { lang }                      = useLang();
  const [translated,  setTranslated]  = useState(temples);
  const [translating, setTranslating] = useState(false);

  useEffect(() => {
    if (!temples || temples.length === 0) {
      setTranslated(temples);
      return;
    }
    if (lang === 'en') {
      setTranslated(temples);
      return;
    }
    setTranslating(true);
    translateTemples(temples, lang)
      .then(setTranslated)
      .finally(() => setTranslating(false));
  }, [temples, lang]);

  return { translated, translating };
}

// Hook for a single temple
export function useTranslatedTemple(temple) {
  const { lang }                      = useLang();
  const [translated,  setTranslated]  = useState(temple);
  const [translating, setTranslating] = useState(false);

  useEffect(() => {
    if (!temple) { setTranslated(temple); return; }
    if (lang === 'en') { setTranslated(temple); return; }
    setTranslating(true);
    translateTemple(temple, lang)
      .then(setTranslated)
      .finally(() => setTranslating(false));
  }, [temple, lang]);

  return { translated, translating };
}