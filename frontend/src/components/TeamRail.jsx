/**
 * 좌측 조 목록 레일.
 * 상태를 배지 대신 작은 램프로 표시합니다. (준비됨 / 개발 중 / 오류)
 */
const LAMP_LABEL = {
  ready: '준비됨',
  not_implemented: '개발 중',
  error: '오류',
}

export default function TeamRail({ teams, activeId, onSelect }) {
  return (
    <nav className="rail" aria-label="조 목록">
      {teams.map((team) => {
        const active = team.id === activeId
        return (
          <button
            key={team.id}
            type="button"
            className={`rail-item${active ? ' is-active' : ''}`}
            aria-current={active ? 'true' : undefined}
            onClick={() => onSelect(team.id)}
          >
            <span className={`lamp lamp--${team.status}`} title={LAMP_LABEL[team.status]} />
            <span className="rail-item__body">
              <span className="rail-item__name">{team.name}</span>
              {team.status !== 'ready' && (
                <span className="rail-item__state">{LAMP_LABEL[team.status]}</span>
              )}
            </span>
          </button>
        )
      })}
    </nav>
  )
}
