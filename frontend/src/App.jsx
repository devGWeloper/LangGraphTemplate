import { useCallback, useEffect, useState } from 'react'

import { fetchTeams, sendChat } from './api'
import ChatPanel from './components/ChatPanel'
import TeamRail from './components/TeamRail'

export default function App() {
  const [teams, setTeams] = useState([])
  const [activeId, setActiveId] = useState(null)
  const [loadError, setLoadError] = useState(null)
  const [loading, setLoading] = useState(true)

  // 조별 대화를 따로 보관합니다. 탭을 옮겨도 각 조의 대화가 그대로 남습니다.
  const [conversations, setConversations] = useState({})
  const [pendingId, setPendingId] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    setLoadError(null)
    try {
      const list = await fetchTeams()
      setTeams(list)
      setActiveId((current) => current ?? list[0]?.id ?? null)
    } catch (error) {
      setLoadError(error.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const active = teams.find((team) => team.id === activeId) ?? null
  const messages = (activeId && conversations[activeId]) || []

  async function handleSend(text) {
    const teamId = activeId
    const history = messages
      .filter((message) => !message.error)
      .map(({ role, content }) => ({ role, content }))

    setConversations((prev) => ({
      ...prev,
      [teamId]: [...(prev[teamId] || []), { role: 'user', content: text }],
    }))
    setPendingId(teamId)

    let reply
    try {
      const body = await sendChat(teamId, text, history)
      reply = {
        role: 'assistant',
        content: body.answer,
        trace: body.trace,
        error: body.error,
      }
    } catch (error) {
      reply = { role: 'assistant', content: '', trace: [], error: error.message }
    }

    setConversations((prev) => ({ ...prev, [teamId]: [...(prev[teamId] || []), reply] }))
    setPendingId(null)
  }

  return (
    <div className="app">
      <header className="masthead">
        <p className="masthead__team">제조AX서비스1팀</p>
        <h1 className="masthead__title">AI 챌린지</h1>
        <p className="masthead__note">LangGraph 로 만든 조별 MultiAgent</p>
      </header>

      {loading && <p className="status">불러오는 중…</p>}

      {loadError && (
        <div className="status status--error">
          <p>{loadError}</p>
          <button type="button" className="chip" onClick={load}>
            다시 불러오기
          </button>
        </div>
      )}

      {!loading && !loadError && teams.length === 0 && (
        <p className="status">
          등록된 조가 없습니다. <code>teams/</code> 폴더를 확인해주세요.
        </p>
      )}

      {active && (
        <main className="workspace">
          <TeamRail teams={teams} activeId={activeId} onSelect={setActiveId} />
          <ChatPanel
            key={active.id}
            team={active}
            messages={messages}
            pending={pendingId === active.id}
            onSend={handleSend}
          />
        </main>
      )}
    </div>
  )
}
