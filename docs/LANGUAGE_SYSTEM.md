# Language System Documentation

This document explains how to add new languages and manage translations in the Homework App.

## Overview

The language system has been refactored to use separate JSON files for each language, making it easy to add new languages and maintain translations.

## File Structure

```
frontend/src/
├── locales/
│   ├── en.json          # English translations
│   ├── es.json          # Spanish translations
│   └── [new-lang].json  # New language files
├── utils/
│   └── languageLoader.js # Language loading utilities
└── contexts/
    └── LanguageContext.jsx # Language context provider
```

## Adding a New Language

### Step 1: Create Translation File

1. Create a new JSON file in `frontend/src/locales/` named with the language code (e.g., `fr.json` for French).
2. Copy the structure from `en.json` and translate all values:

```json
{
  "nav.dashboard": "Tableau de bord",
  "nav.classes": "Classes",
  "nav.schedule": "Horaire",
  "nav.homework": "Devoirs",
  "nav.signOut": "Se déconnecter",
  "app.title": "App de Devoirs",
  
  "dashboard.title": "Tableau de bord",
  "dashboard.subtitle": "Aperçu de vos classes et devoirs",
  ...
}
```

### Step 2: Update Language Configuration

Edit `frontend/src/utils/languageLoader.js` and add your language to the `availableLanguages` object:

```javascript
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
  },
  fr: {  // Add new language
    code: 'fr',
    name: 'Français',
    flag: '🇫🇷'
  }
};
```

### Step 3: Test the Language

1. Start the development server: `npm run dev`
2. Open the language selector in the UI
3. Verify your new language appears and works correctly

## Translation Keys Structure

Translation keys are organized hierarchically using dot notation:

- `nav.*` - Navigation items
- `dashboard.*` - Dashboard page
- `classes.*` - Classes page
- `homework.*` - Homework page
- `login.*` - Login page
- `common.*` - Common UI elements
- `message.*` - Success/error messages
- `filter.*` - Filter options
- `priority.*` - Priority levels
- `status.*` - Status options
- `classType.*` - Class type options

## Best Practices

### 1. Consistent Key Naming
Use clear, hierarchical key names:
```json
{
  "classes.title": "Classes",
  "classes.addClass": "Add Class",
  "classes.editClass": "Edit Class",
  "classes.created": "Class created successfully"
}
```

### 2. Placeholder Support
Some translations may need placeholders (handled by the consuming component):
```json
{
  "homework.dueIn": "Due in {days} days",
  "classes.studentsCount": "{count} students"
}
```

### 3. Proper Escaping
Escape special characters in JSON:
```json
{
  "dashboard.confirmMessage": "Are you sure you want to delete?\\n\\nThis action cannot be undone!"
}
```

### 4. Fallback Handling
The system automatically falls back to:
1. English translation if the key doesn't exist in the selected language
2. The key itself if no translation is found at all

## Technical Details

### Dynamic Loading
- Translation files are loaded dynamically using ES6 imports
- Files are cached after first load for performance
- Vite automatically code-splits language files

### Context Usage
Use the `useLanguage` hook in React components:

```jsx
import { useLanguage } from '../contexts/LanguageContext'

function MyComponent() {
  const { t, language, changeLanguage, loading } = useLanguage()
  
  if (loading) {
    return <div>Loading translations...</div>
  }
  
  return (
    <div>
      <h1>{t('dashboard.title')}</h1>
      <button onClick={() => changeLanguage('fr')}>
        Switch to French
      </button>
    </div>
  )
}
```

### Available Properties
- `t(key)` - Translate a key
- `language` - Current language code
- `changeLanguage(code)` - Switch language
- `loading` - Whether translations are loading
- `availableLanguages` - Array of supported language codes

## Validation

To validate your translations:

1. **Build Test**: Run `npm run build` to ensure no syntax errors
2. **Missing Keys**: Check browser console for missing translation warnings
3. **UI Test**: Navigate through all pages to verify translations display correctly

## Migration Notes

The old hardcoded translation system has been completely replaced. All translations are now externalized to JSON files, making maintenance much easier.

### Before (Old System)
```jsx
const translations = {
  en: { "key": "value" },
  es: { "key": "valor" }
}
```

### After (New System)
```
locales/en.json: { "key": "value" }
locales/es.json: { "key": "valor" }
```

This new system supports:
- Easy addition of new languages
- Better organization of translations
- Code splitting for better performance
- IDE support for JSON editing
- Version control friendly diffs