import type { FC } from 'react'
import { memo } from 'react'
import { useTranslation } from 'react-i18next'

import { useNodesReadOnly } from '@/app/components/workflow/hooks'
import { ArrowUturnLeft, ArrowUturnRight } from '@/app/components/base/icons/src/vender/solid/arrows'

export type UndoRedoComponentProps = { handleUndo: () => void; handleRedo: () => void }
const UndoRedoComponent: FC<UndoRedoComponentProps> = ({ handleUndo, handleRedo }) => {
  const { t } = useTranslation()

  const { nodesReadOnly } = useNodesReadOnly()

  return (
    <div className='flex items-center px-0.5 h-8 rounded-lg border-[0.5px] border-gray-200 bg-white shadow-xs mx-2'>

      <div
        className={`
        flex items-center px-1.5 h-7 rounded-md text-[13px] font-medium text-primary-600
        hover:bg-primary-50 cursor-pointer select-none
        ${nodesReadOnly && 'bg-primary-50 opacity-50 !cursor-not-allowed'}
      `}
        onClick={() => !nodesReadOnly && handleUndo()}
      >
        <ArrowUturnLeft className='mr-1 px-1 h-4' />
        {t('workflow.common.undo')}
      </div>

      <div
        className={`
        flex items-center px-1.5 h-7 rounded-md text-[13px] font-medium text-primary-600
        hover:bg-primary-50 cursor-pointer select-none
        ${nodesReadOnly && 'bg-primary-50 opacity-50 !cursor-not-allowed'}
      `}
        onClick={() => !nodesReadOnly && handleRedo()}
      >
        <ArrowUturnRight className='mr-1 px-1 h-4' />
        {t('workflow.common.redo')}

      </div>
    </div>
  )
}

export default memo(UndoRedoComponent)
