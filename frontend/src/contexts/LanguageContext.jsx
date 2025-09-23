import React, { createContext, useContext, useState, useEffect } from 'react'
import { loadTranslations, getAvailableLanguageCodes, isLanguageSupported } from '../utils/languageLoader'

const LanguageContext = createContext()

export const useLanguage = () => {
  const context = useContext(LanguageContext)
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider')
  }
  return context
}

export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState(() => {
    // Get language from localStorage or default to English
    const saved = localStorage.getItem('language') || 'en'
    return isLanguageSupported(saved) ? saved : 'en'
  })
  
  const [translations, setTranslations] = useState({})
  const [loading, setLoading] = useState(true)

  // Load translations when language changes
  useEffect(() => {
    const loadLanguageData = async () => {
      setLoading(true)
      try {
        const translationData = await loadTranslations(language)
        setTranslations(translationData)
      } catch (error) {
        console.error('Failed to load translations:', error)
        // Fallback to empty translations
        setTranslations({})
      } finally {
        setLoading(false)
      }
    }

    loadLanguageData()
  }, [language])

  // Save language preference to localStorage
  useEffect(() => {
    localStorage.setItem('language', language)
  }, [language])

  const t = (key) => {
    if (loading) {
      return key // Return key while loading
    }
    return translations[key] || key
  }

  const changeLanguage = (newLanguage) => {
    if (isLanguageSupported(newLanguage)) {
      setLanguage(newLanguage)
    } else {
      console.warn(`Language '${newLanguage}' is not supported`)
    }
  }

  const value = {
    language,
    changeLanguage,
    t,
    loading,
    availableLanguages: getAvailableLanguageCodes()
  }

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  )
}