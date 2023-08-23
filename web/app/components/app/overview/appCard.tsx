'use client'
import type { FC } from 'react'
import React, { useMemo, useState } from 'react'
import {
  Cog8ToothIcon,
  DocumentTextIcon,
  PaintBrushIcon,
  RocketLaunchIcon,
} from '@heroicons/react/24/outline'
import { usePathname, useRouter } from 'next/navigation'
import { useTranslation } from 'react-i18next'
import SettingsModal from './settings'
import EmbeddedModal from './embedded'
import CustomizeModal from './customize'
import style from './style.module.css'
import type { ConfigParams } from './settings'
import Tooltip from '@/app/components/base/tooltip'
import AppBasic from '@/app/components/app-sidebar/basic'
import { asyncRunSafe, randomString } from '@/utils'
import Button from '@/app/components/base/button'
import Tag from '@/app/components/base/tag'
import Switch from '@/app/components/base/switch'
import Divider from '@/app/components/base/divider'
import CopyFeedback from '@/app/components/base/copy-feedback'
import SecretKeyButton from '@/app/components/develop/secret-key/secret-key-button'
import type { AppDetailResponse } from '@/models/app'
import { AppType } from '@/types/app'
import { useAppContext } from '@/context/app-context'

export type IAppCardProps = {
  className?: string
  appInfo: AppDetailResponse
  cardType?: 'api' | 'webapp'
  customBgColor?: string
  onChangeStatus: (val: boolean) => Promise<void>
  onSaveSiteConfig?: (params: ConfigParams) => Promise<void>
  onGenerateCode?: () => Promise<void>
}

const EmbedIcon: FC<{ className?: string }> = ({ className = '' }) => {
  return <div className={`${style.codeBrowserIcon} ${className}`}></div>
}

function AppCard({
  appInfo,
  cardType = 'webapp',
  customBgColor,
  onChangeStatus,
  onSaveSiteConfig,
  onGenerateCode,
  className,
}: IAppCardProps) {
  const router = useRouter()
  const pathname = usePathname()
  const { currentWorkspace, isCurrentWorkspaceManager } = useAppContext()
  const [showSettingsModal, setShowSettingsModal] = useState(false)
  const [showEmbedded, setShowEmbedded] = useState(false)
  const [showCustomizeModal, setShowCustomizeModal] = useState(false)
  const [genLoading, setGenLoading] = useState(false)
  const { t } = useTranslation()

  const OPERATIONS_MAP = useMemo(() => {
    const operationsMap = {
      webapp: [
        { opName: t('appOverview.overview.appInfo.preview'), opIcon: RocketLaunchIcon },
        { opName: t('appOverview.overview.appInfo.customize.entry'), opIcon: PaintBrushIcon },
      ] as { opName: string; opIcon: any }[],
      api: [{ opName: t('appOverview.overview.apiInfo.doc'), opIcon: DocumentTextIcon }],
      app: [],
    }
    if (appInfo.mode === AppType.chat)
      operationsMap.webapp.push({ opName: t('appOverview.overview.appInfo.embedded.entry'), opIcon: EmbedIcon })

    if (isCurrentWorkspaceManager)
      operationsMap.webapp.push({ opName: t('appOverview.overview.appInfo.settings.entry'), opIcon: Cog8ToothIcon })

    return operationsMap
  }, [isCurrentWorkspaceManager, appInfo, t])

  const isApp = cardType === 'webapp'
  const basicName = isApp
    ? appInfo?.site?.title
    : t('appOverview.overview.apiInfo.title')
  const runningStatus = isApp ? appInfo.enable_site : appInfo.enable_api
  const { app_base_url, access_token } = appInfo.site ?? {}
  const appUrl = `${app_base_url}/${appInfo.mode}/${access_token}`
  const apiUrl = appInfo?.api_base_url

  let bgColor = 'bg-primary-50 bg-opacity-40'
  if (cardType === 'api')
    bgColor = 'bg-purple-50'

  const genClickFuncByName = (opName: string) => {
    switch (opName) {
      case t('appOverview.overview.appInfo.preview'):
        return () => {
          window.open(appUrl, '_blank')
        }
      case t('appOverview.overview.appInfo.customize.entry'):
        return () => {
          setShowCustomizeModal(true)
        }
      case t('appOverview.overview.appInfo.settings.entry'):
        return () => {
          setShowSettingsModal(true)
        }
      case t('appOverview.overview.appInfo.embedded.entry'):
        return () => {
          setShowEmbedded(true)
        }
      default:
        // jump to page develop
        return () => {
          const pathSegments = pathname.split('/')
          pathSegments.pop()
          router.push(`${pathSegments.join('/')}/develop`)
        }
    }
  }

  const onGenCode = async () => {
    setGenLoading(true)
    await asyncRunSafe(onGenerateCode?.() as any)
    setGenLoading(false)
  }

  return (
    <div
      className={`min-w-max shadow-xs border-[0.5px] rounded-lg border-gray-200 ${
        className ?? ''
      }`}
    >
      <div className={`px-6 py-5 ${customBgColor ?? bgColor} rounded-lg`}>
        <div className="mb-2.5 flex flex-row items-start justify-between">
          <AppBasic
            iconType={cardType}
            icon={appInfo.icon}
            icon_background={appInfo.icon_background}
            name={basicName}
            type={
              isApp
                ? t('appOverview.overview.appInfo.explanation')
                : t('appOverview.overview.apiInfo.explanation')
            }
          />
          <div className="flex flex-row items-center h-9">
            <Tag className="mr-2" color={runningStatus ? 'green' : 'yellow'}>
              {runningStatus
                ? t('appOverview.overview.status.running')
                : t('appOverview.overview.status.disable')}
            </Tag>
            <Switch defaultValue={runningStatus} onChange={onChangeStatus} disabled={currentWorkspace?.role === 'normal'} />
          </div>
        </div>
        <div className="flex flex-col justify-center py-2">
          <div className="py-1">
            <div className="pb-1 text-xs text-gray-500">
              {isApp
                ? t('appOverview.overview.appInfo.accessibleAddress')
                : t('appOverview.overview.apiInfo.accessibleAddress')}
            </div>
            <div className="w-full h-9 pl-2 pr-0.5 py-0.5 bg-black bg-opacity-[0.02] rounded-lg border border-black border-opacity-5 justify-start items-center inline-flex">
              <div className="h-4 px-2 justify-start items-start gap-2 flex flex-1">
                <div className="text-gray-700 text-xs font-medium">
                  {isApp ? appUrl : apiUrl}
                </div>
              </div>
              <Divider type="vertical" className="!h-3.5 shrink-0 !mx-0.5" />
              <CopyFeedback
                content={isApp ? appUrl : apiUrl}
                selectorId={randomString(8)}
                className={'hover:bg-gray-200'}
              />
              {/* button copy link/ button regenerate */}
              {isApp && isCurrentWorkspaceManager && (
                <Tooltip
                  content={t('appOverview.overview.appInfo.regenerate') || ''}
                  selector={`code-generate-${randomString(8)}`}
                >
                  <div
                    className="w-8 h-8 ml-0.5 cursor-pointer hover:bg-gray-200 rounded-lg"
                    onClick={onGenCode}
                  >
                    <div
                      className={`w-full h-full ${style.refreshIcon} ${
                        genLoading ? style.generateLogo : ''
                      }`}
                    ></div>
                  </div>
                </Tooltip>
              )}
            </div>
          </div>
        </div>
        <div className={'pt-2 flex flex-row items-center'}>
          {!isApp && <SecretKeyButton className='flex-shrink-0 !h-8 bg-white mr-2' textCls='!text-gray-700 font-medium' iconCls='stroke-[1.2px]' appId={appInfo.id} />}
          {OPERATIONS_MAP[cardType].map((op) => {
            const disabled
              = op.opName === t('appOverview.overview.appInfo.settings.entry')
                ? false
                : !runningStatus
            return (
              <Button
                className="mr-2 border-[0.5px] !h-8 hover:outline hover:outline-[0.5px] hover:outline-gray-300 text-gray-700 font-medium bg-white shadow-[0px_1px_2px_0px_rgba(16,24,40,0.05)]"
                key={op.opName}
                onClick={genClickFuncByName(op.opName)}
                disabled={disabled}
              >
                <Tooltip
                  content={
                    t('appOverview.overview.appInfo.preUseReminder') ?? ''
                  }
                  selector={`op-btn-${randomString(16)}`}
                  className={disabled ? 'mt-[-8px]' : '!hidden'}
                >
                  <div className="flex flex-row items-center">
                    <op.opIcon className="h-4 w-4 mr-1.5 stroke-[1.8px]" />
                    <span className="text-[13px]">{op.opName}</span>
                  </div>
                </Tooltip>
              </Button>
            )
          })}
        </div>
      </div>
      {isApp
        ? (
          <>
            <SettingsModal
              appInfo={appInfo}
              isShow={showSettingsModal}
              onClose={() => setShowSettingsModal(false)}
              onSave={onSaveSiteConfig}
            />
            <EmbeddedModal
              isShow={showEmbedded}
              onClose={() => setShowEmbedded(false)}
              appBaseUrl={app_base_url}
              accessToken={access_token}
            />
            <CustomizeModal
              isShow={showCustomizeModal}
              linkUrl=""
              onClose={() => setShowCustomizeModal(false)}
              appId={appInfo.id}
              mode={appInfo.mode}
            />
          </>
        )
        : null}
    </div>
  )
}

export default AppCard
