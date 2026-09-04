import DOMPurify from 'dompurify'
import { marked } from 'marked'

import TraceRail from './TraceRail'

marked.setOptions({ breaks: true, gfm: true })

function renderMarkdown(text) {
  return DOMPurify.sanitize(marked.parse(text ?? ''))
}

export default function MessageBubble({ message }) {
  if (message.role === 'user') {
    return (
      <div className="msg msg--user">
        <div className="bubble bubble--user">{message.content}</div>
      </div>
    )
  }

  if (message.error) {
    // 접속 정보 미설정은 조원 코드 잘못이 아니므로 따로 안내합니다.
    const isConfigError = message.error.startsWith('LLMConfigError')

    return (
      <div className="msg msg--agent">
        <div className="bubble bubble--error">
          <p className="bubble--error__title">
            {isConfigError
              ? 'LLM 접속 정보가 설정되지 않았습니다'
              : '이 조의 코드에서 문제가 생겼습니다'}
          </p>
          {isConfigError ? (
            <p className="bubble--error__body">
              <code>.env.example</code> 을 복사해 <code>.env</code> 를 만들고{' '}
              <code>LLM_BASE_URL</code>, <code>LLM_API_KEY</code>, <code>LLM_MODEL</code> 을 채운 뒤
              서버를 다시 실행해주세요.
            </p>
          ) : (
            <pre className="bubble--error__detail">{message.error}</pre>
          )}
        </div>
        <TraceRail trace={message.trace} />
      </div>
    )
  }

  return (
    <div className="msg msg--agent">
      <div
        className="bubble bubble--agent"
        dangerouslySetInnerHTML={{ __html: renderMarkdown(message.content) }}
      />
      <TraceRail trace={message.trace} />
    </div>
  )
}
