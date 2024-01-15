import type { FC, ReactNode } from 'react'
import { useTranslation } from 'react-i18next'
import type { ChatItem } from '../types'
import { useChatContext } from '../context'
import { AnswerTriangle } from '@/app/components/base/icons/src/vender/solid/general'
import LoadingAnim from '@/app/components/app/chat/loading-anim'
import { MessageHeartCircle } from '@/app/components/base/icons/src/vender/solid/communication'
import { Markdown } from '@/app/components/base/markdown'
import { formatNumber } from '@/utils/format'
import Citation from '@/app/components/app/chat/citation'

type AnswerProps = {
  item: ChatItem
  icon?: ReactNode
  responsing?: boolean
}
const Answer: FC<AnswerProps> = ({
  item,
  icon,
  responsing,
}) => {
  const { t } = useTranslation()
  const { config } = useChatContext()
  const {
    isOpeningStatement,
    content,
    citation,
    agent_thoughts,
    more,
  } = item
  const isThinking = !content && agent_thoughts && agent_thoughts?.length > 0 && !agent_thoughts.some(agent => agent.thought === '[DONE]')

  return (
    <div className='flex mb-2 last:mb-0'>
      <div className='shrink-0 relative w-10 h-10'>
        {
          icon || (
            <div className='flex items-center justify-center w-full h-full rounded-full bg-[#d5f5f6] border-[0.5px] border-black/5 text-xl'>
              🤖
            </div>
          )
        }
        {
          responsing && (
            <div className='absolute -top-[3px] -left-[3px] pl-[6px] flex items-center w-4 h-4 bg-white rounded-full shadow-xs border-[0.5px] border-gray-50'>
              <LoadingAnim type='avatar' />
            </div>
          )
        }
      </div>
      <div className='group ml-4'>
        <div className='relative pr-10'>
          <AnswerTriangle className='absolute -left-2 top-0 w-2 h-3 text-gray-100' />
          <div className='inline-block px-4 py-3 bg-gray-100 rounded-b-2xl rounded-tr-2xl text-sm text-gray-900'>
            {
              isOpeningStatement && (
                <div className='flex items-center mb-1 h-[18px]'>
                  <MessageHeartCircle className='mr-1 w-3 h-3 text-gray-500' />
                  <div className='text-xs text-gray-500'>{t('appDebug.openingStatement.title')}</div>
                </div>
              )
            }
            {
              !content && responsing && (
                <div className='flex items-center justify-center w-6 h-5'>
                  <LoadingAnim type='text' />
                </div>
              )
            }
            {
              content && (
                <div>
                  <Markdown content={content} />
                </div>
              )
            }
            {
              !!citation?.length && !isThinking && config.retriever_resource?.enabled && !responsing && (
                <Citation data={citation} showHitInfo />
              )
            }
          </div>
        </div>
        <div className='flex items-center mt-1 h-[18px] text-xs text-gray-400 opacity-0 group-hover:opacity-100'>
          {
            more && (
              <>
                <div className='mr-2'>{`${t('appLog.detail.timeConsuming')} ${more.latency}${t('appLog.detail.second')}`}</div>
                <div
                  className='turncate'
                  title={`${t('appLog.detail.tokenCost')} ${formatNumber(more.tokens)}`}
                >
                  {`${t('appLog.detail.tokenCost')} ${formatNumber(more.tokens)}`}
                </div>
                <div className='mx-2'>·</div>
                <div>{more.time}</div>
              </>
            )
          }
        </div>
      </div>
    </div>
  )
}

export default Answer
