'use client'

import type { FC } from 'react'
import React from 'react'
import { changeLanguage } from '@/i18n/i18next-config'
import I18NContext from '@/context/i18n'
import type { Locale } from '@/i18n'
import { getLocaleOnClient, setLocaleOnClient } from '@/i18n/client'

export type II18nProps = {
  locale: Locale
  dictionary: Record<string, any>
  children: React.ReactNode
  // setLocaleOnClient: (locale: Locale) => void
}
const I18n: FC<II18nProps> = ({
  dictionary,
  children,
  locale,
}) => {
  const clientLocale = getLocaleOnClient()

  // force to change language if server have the locale to resolve the UI hydrate error
  locale && changeLanguage(locale)

  return (
    <I18NContext.Provider value={{
      locale: locale || clientLocale,
      i18n: dictionary,
      setLocaleOnClient,
    }}>
      {children}
    </I18NContext.Provider>
  )
}
export default React.memo(I18n)
