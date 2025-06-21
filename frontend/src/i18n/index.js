import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const savedLanguage = localStorage.getItem('language') || 'en';

import en from './en.json';
import es from './es.json';
import fr from './fr.json';
import de from './de.json';
import tr from './tr.json';

// Initialize i18next
i18n
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      es: { translation: es },
      fr: { translation: fr },
      de: { translation: de },
      tr: { translation: tr }
    },
    lng: savedLanguage,
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    }
  });

// Persist language changes
i18n.on('languageChanged', (lng) => {
  localStorage.setItem('language', lng);
});

export default i18n;
