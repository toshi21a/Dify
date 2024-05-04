'use client'
import type { FC } from 'react'
import React from 'react'
import { useContext } from 'use-context-selector'
import { useTranslation } from 'react-i18next'
import RadioGroup from './radio-group'
import ConfigContext from '@/context/debug-configuration'
import { IsExtractAudio, IsExtractVideo, Resolution, TransferMethod } from '@/types/app'
import ParamItem from '@/app/components/base/param-item'
import Tooltip from '@/app/components/base/tooltip'
import { HelpCircle } from '@/app/components/base/icons/src/vender/line/general'

const MIN = 1
const MAX = 6
const ParamConfigContent: FC = () => {
  const { t } = useTranslation()

  const {
    visionConfig,
    setVisionConfig,
  } = useContext(ConfigContext)

  const transferMethod = (() => {
    if (!visionConfig.transfer_methods || visionConfig.transfer_methods.length === 2)
      return TransferMethod.all

    return visionConfig.transfer_methods[0]
  })()

  return (
    <div>
      <div className='leading-6 text-base font-semibold text-gray-800'>{t('appDebug.vision.visionSettings.title')}</div>
      <div className='pt-3 space-y-6'>
        <div>
          <div className='mb-2 flex items-center space-x-1'>
            <div className='leading-[18px] text-[13px] font-semibold text-gray-800'>{t('appDebug.vision.visionSettings.resolution')}</div>
            <Tooltip htmlContent={<div className='w-[180px]'>
              {t('appDebug.vision.visionSettings.resolutionTooltip').split('\n').map(item => (
                <div key={item}>{item}</div>
              ))}
            </div>} selector='config-resolution-tooltip'>
              <HelpCircle className='w-[14px] h-[14px] text-gray-400'/>
            </Tooltip>
          </div>
          <RadioGroup
            className='space-x-3'
            options={[
              {
                label: t('appDebug.vision.visionSettings.high'),
                value: Resolution.high,
              },
              {
                label: t('appDebug.vision.visionSettings.low'),
                value: Resolution.low,
              },
            ]}
            value={visionConfig.detail}
            onChange={(value: Resolution) => {
              setVisionConfig({
                ...visionConfig,
                detail: value,
              })
            }}
          />
        </div>
        <div>
          <div
            className='mb-2 leading-[18px] text-[13px] font-semibold text-gray-800'>{t('appDebug.vision.visionSettings.uploadMethod')}</div>
          <RadioGroup
            className='space-x-3'
            options={[
              {
                label: t('appDebug.vision.visionSettings.both'),
                value: TransferMethod.all,
              },
              {
                label: t('appDebug.vision.visionSettings.localUpload'),
                value: TransferMethod.local_file,
              },
              {
                label: t('appDebug.vision.visionSettings.url'),
                value: TransferMethod.remote_url,
              },
            ]}
            value={transferMethod}
            onChange={(value: TransferMethod) => {
              if (value === TransferMethod.all) {
                setVisionConfig({
                  ...visionConfig,
                  transfer_methods: [TransferMethod.remote_url, TransferMethod.local_file],
                })
                return
              }
              setVisionConfig({
                ...visionConfig,
                transfer_methods: [value],
              })
            }}
          />
        </div>
        <div>
          <ParamItem
            id='upload_limit'
            className=''
            name={t('appDebug.vision.visionSettings.uploadLimit')}
            noTooltip
            {...{
              default: 2,
              step: 1,
              min: MIN,
              max: MAX,
            }}
            value={visionConfig.number_limits}
            enable={true}
            onChange={(_key: string, value: number) => {
              if (!value)
                return

              setVisionConfig({
                ...visionConfig,
                number_limits: value,
              })
            }}
          />
        </div>
        <div className="page-break-before">{t('appDebug.vision.visionSettings.video_extraction')}</div>
        <div>
          <div className='mb-2 flex items-center space-x-1'>
            <div className='leading-[18px] text-[13px] font-semibold text-gray-800'>{t('appDebug.vision.visionSettings.extractAudio')}</div>
            <Tooltip htmlContent={<div className='w-[180px]'>
              {t('appDebug.vision.visionSettings.extractAudiotip').split('\n').map(item => (
                <div key={item}>{item}</div>
              ))}
            </div>} selector='config-extractaudio-tooltip'>
              <HelpCircle className='w-[14px] h-[14px] text-gray-400'/>
            </Tooltip>
          </div>
          <RadioGroup
            className='space-x-3'
            options={[
              {
                label: t('appDebug.vision.visionSettings.InextractAudio'),
                value: IsExtractAudio.enabled,
              },
              {
                label: t('appDebug.vision.visionSettings.ExextractAudio'),
                value: IsExtractAudio.diabled,
              },
            ]}
            value={visionConfig.extract_audio}
            onChange={(value: IsExtractAudio) => {
              setVisionConfig({
                ...visionConfig,
                extract_audio: value,
              })
            }}
          />
        </div>
        <div>
          <div className='mb-2 flex items-center space-x-1'>
            <div className='leading-[18px] text-[13px] font-semibold text-gray-800'>{t('appDebug.vision.visionSettings.extractVideo')}</div>
            <Tooltip htmlContent={<div className='w-[180px]'>
              {t('appDebug.vision.visionSettings.extractVideotip').split('\n').map(item => (
                <div key={item}>{item}</div>
              ))}
            </div>} selector='config-extractvideo-tooltip'>
              <HelpCircle className='w-[14px] h-[14px] text-gray-400'/>
            </Tooltip>
          </div>
          <RadioGroup
            className='space-x-3'
            options={[
              {
                label: t('appDebug.vision.visionSettings.InextractVideo'),
                value: IsExtractVideo.enabled,
              },
              {
                label: t('appDebug.vision.visionSettings.ExextractVideo'),
                value: IsExtractVideo.diabled,
              },
            ]}
            value={visionConfig.extract_video}
            onChange={(value: IsExtractAudio) => {
              setVisionConfig({
                ...visionConfig,
                extract_video: value,
              })
            }}
          />
        </div>
        { visionConfig.extract_video === IsExtractVideo.enabled && (
          <div>
            <ParamItem
              id='MaxCollectFrames'
              className=''
              name={t('appDebug.vision.visionSettings.MaxCollectFrames')}
              noTooltip
              {...{
                default: 20,
                step: 1,
                min: 3,
                max: 100,
              }}
              value={visionConfig.max_collect_frames}
              enable={true}
              onChange={(_key: string, value: number) => {
                if (!value)
                  return

                setVisionConfig({
                  ...visionConfig,
                  max_collect_frames: value,
                })
              }}
            />
            <ParamItem
              id='blurThreshold'
              className=''
              name={t('appDebug.vision.visionSettings.blurThreshold')}
              noTooltip
              {...{
                default: 800,
                step: 50,
                min: 500,
                max: 2000,
              }}
              value={visionConfig.blur_threshold}
              enable={true}
              onChange={(_key: string, value: number) => {
                if (!value)
                  return

                setVisionConfig({
                  ...visionConfig,
                  blur_threshold: value,
                })
              }}
            />
            <ParamItem
              id='similarityThreshold'
              className=''
              name={t('appDebug.vision.visionSettings.similarityThreshold')}
              noTooltip
              {...{
                default: 0.7,
                step: 0.1,
                min: 0.1,
                max: 1.0,
              }}
              value={visionConfig.similarity_threshold}
              enable={true}
              onChange={(_key: string, value: number) => {
                if (!value)
                  return

                setVisionConfig({
                  ...visionConfig,
                  similarity_threshold: value,
                })
              }}
            />
          </div>
        )}
      </div>
    </div>
  )
}

export default React.memo(ParamConfigContent)
