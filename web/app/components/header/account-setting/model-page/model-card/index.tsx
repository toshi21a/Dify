import type { FC, ReactElement } from 'react'
import { useTranslation } from 'react-i18next'
import { useContext } from 'use-context-selector'
import type { I18NText } from '../declarations'
import Indicator from '../../../indicator'
import PrioritySelector from './PrioritySelector'
import { IS_CE_EDITION } from '@/config'
import I18n from '@/context/i18n'
import Button from '@/app/components/base/button'
import { InfoCircle, Plus } from '@/app/components/base/icons/src/vender/line/general'
import Tooltip from '@/app/components/base/tooltip'

type ModelCardProps = {
  provider: { key: string; type: string; bgColor: string; icon: ReactElement; desc: I18NText; iconText?: ReactElement }
  onOpenModal: () => void
}

const ModelCard: FC<ModelCardProps> = ({
  provider,
  onOpenModal,
}) => {
  const { locale } = useContext(I18n)
  const { t } = useTranslation()

  return (
    <div className='rounded-xl border-[0.5px] border-gray-200 shadow-xs'>
      <div className={`flex px-4 pt-4 pb-3 rounded-t-lg ${provider.bgColor}`}>
        <div className='mr-3'>
          <div className='mb-1'>
            {provider.iconText}
          </div>
          <div className='text-xs text-black opacity-60'>{provider.desc[locale]}</div>
        </div>
        {provider.icon}
      </div>
      {
        !IS_CE_EDITION && (
          <div className='flex justify-between px-4 py-3 border-b-[0.5px] border-b-[rgba(0, 0, 0, 0.5)]'>
            <div>
              <div className='flex items-center mb-1 h-5'>
                <div className='mr-1 text-xs font-medium text-gray-500'>{t('common.modelProvider.card.quota')}</div>
                <div className='px-1.5 bg-primary-50 rounded-md text-xs font-semibold text-primary-600'>{t('common.modelProvider.card.onTrial')}</div>
              </div>
              <div className='flex items-center text-gray-700'>
                <div className='mr-1 text-sm font-medium'>200</div>
                <div className='mr-1 text-sm'>{t('common.modelProvider.card.callTimes')}</div>
                <Tooltip
                  selector={`setting-model-card-${provider.key}`}
                  htmlContent={
                    <div className='w-[261px] text-gray-500'>{t('common.modelProvider.card.tip')}</div>
                  }
                >
                  <InfoCircle className='w-3 h-3 text-gray-400 hover:text-gray-700' />
                </Tooltip>
              </div>
            </div>
            <Button className='mt-1.5 !px-3 !h-8 !text-[13px] font-medium rounded-lg' type='primary'>{t('common.modelProvider.card.buyQuota')}</Button>
          </div>
        )
      }
      <div
        className='inline-flex items-center px-4 h-12 text-gray-500 cursor-pointer hover:text-primary-600'
        onClick={onOpenModal}
      >
        <Plus className='mr-1.5 w-4 h-4'/>
        <div className='text-xs font-medium'>{t('common.modelProvider.addApiKey')}</div>
      </div>
      <div className='flex items-center px-4 h-12'>
        <Indicator color='green' className='mr-2' />
        <div className='grow text-[13px] font-medium text-gray-700'>API key</div>
        <div className='mr-1 px-2 leading-6 rounded-md text-xs font-medium text-gray-500 hover:bg-gray-50 cursor-pointer'>{t('common.operation.edit')}</div>
        <PrioritySelector />
      </div>
    </div>
  )
}

export default ModelCard
