import { useEffect, useRef, useState } from 'react'

import MessageBubble from './MessageBubble'
import { TracePending } from './TraceRail'

function NotReady({ team }) {
  if (team.status === 'error') {
    return (
      <div className="notice notice--error">
        <p className="notice__title">이 조의 코드를 불러오지 못했습니다</p>
        <p className="notice__body">
          <code>teams/{team.id}/workflow.py</code> 를 열어 아래 오류를 고쳐주세요. 고치고 저장하면
          서버가 다시 뜹니다.
        </p>
        <pre className="notice__detail">{team.error}</pre>
      </div>
    )
  }

  return (
    <div className="notice">
      <p className="notice__title">아직 개발 중입니다</p>
      <p className="notice__body">
        <code>teams/{team.id}/workflow.py</code> 의 <code>build_graph()</code> 를 완성하면 이 자리에서
        바로 대화할 수 있습니다. 만드는 방법은 0조 예제를 참고하세요.
      </p>
    </div>
  )
}

export default function ChatPanel({ team, messages, pending, onSend }) {
  const [draft, setDraft] = useState('')
  const scrollRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    const box = scrollRef.current
    if (box) box.scrollTop = box.scrollHeight
  }, [messages, pending])

  const ready = team.status === 'ready'
  const empty = messages.length === 0

  function submit(event) {
    event.preventDefault()
    const text = draft.trim()
    if (!text || pending || !ready) return
    setDraft('')
    onSend(text)
  }

  function useExample(text) {
    setDraft(text)
    inputRef.current?.focus()
  }

  return (
    <section className="chat" aria-label={`${team.name} 대화`}>
      <header className="chat__head">
        <h2 className="chat__title">{team.name}</h2>
        {team.description && <p className="chat__desc">{team.description}</p>}
      </header>

      <div className="chat__scroll" ref={scrollRef}>
        {!ready && <NotReady team={team} />}

        {ready && empty && (
          <div className="opening">
            <p className="opening__text">무엇이든 물어보세요.</p>
            {team.examples.length > 0 && (
              <ul className="chips">
                {team.examples.map((example) => (
                  <li key={example}>
                    <button type="button" className="chip" onClick={() => useExample(example)}>
                      {example}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        {messages.map((message, index) => (
          <MessageBubble key={index} message={message} />
        ))}

        {pending && <TracePending />}
      </div>

      <form className="composer" onSubmit={submit}>
        <input
          ref={inputRef}
          className="composer__input"
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder={ready ? '메시지를 입력하세요' : '이 조는 아직 대화할 수 없습니다'}
          disabled={!ready || pending}
          aria-label="메시지"
        />
        <button className="composer__send" type="submit" disabled={!ready || pending || !draft.trim()}>
          {pending ? '실행 중' : '보내기'}
        </button>
      </form>
    </section>
  )
}
