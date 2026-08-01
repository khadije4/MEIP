import '@testing-library/jest-dom/vitest'
import { afterEach, beforeEach } from 'vitest'
import { cleanup } from '@testing-library/react'
import i18n from '../i18n'

beforeEach(async () => {
  window.localStorage.clear()
  await i18n.changeLanguage('fr')
  document.documentElement.lang = 'fr'
  document.documentElement.dir = 'ltr'
})
afterEach(() => cleanup())
