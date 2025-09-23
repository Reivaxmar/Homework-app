/**
 * Language loader utility for dynamic translation file loading
 */

// Available languages configuration
export const availableLanguages = {
  en: {
    code: 'en',
    name: 'English',
    flag: '🇺🇸'
  },
  es: {
    code: 'es', 
    name: 'Español',
    flag: '🇪🇸'
  }
};

// Cache for loaded translations
const translationCache = new Map();

/**
 * Load translation file for given language
 * @param {string} languageCode - Language code (e.g., 'en', 'es')
 * @returns {Promise<Object>} Translation object
 */
export async function loadTranslations(languageCode) {
  // Check cache first
  if (translationCache.has(languageCode)) {
    return translationCache.get(languageCode);
  }

  try {
    // Dynamically import the language file
    const translations = await import(`../locales/${languageCode}.json`);
    const translationData = translations.default || translations;
    
    // Cache the loaded translations
    translationCache.set(languageCode, translationData);
    
    return translationData;
  } catch (error) {
    console.warn(`Failed to load translations for language: ${languageCode}`, error);
    
    // Fallback to English if available and not already trying English
    if (languageCode !== 'en') {
      console.warn(`Falling back to English translations`);
      return loadTranslations('en');
    }
    
    // Return empty object as final fallback
    return {};
  }
}

/**
 * Get list of available language codes
 * @returns {string[]} Array of language codes
 */
export function getAvailableLanguageCodes() {
  return Object.keys(availableLanguages);
}

/**
 * Get language metadata
 * @param {string} languageCode - Language code
 * @returns {Object} Language metadata
 */
export function getLanguageMetadata(languageCode) {
  return availableLanguages[languageCode] || availableLanguages.en;
}

/**
 * Validate if language code is supported
 * @param {string} languageCode - Language code to validate
 * @returns {boolean} True if supported
 */
export function isLanguageSupported(languageCode) {
  return languageCode in availableLanguages;
}