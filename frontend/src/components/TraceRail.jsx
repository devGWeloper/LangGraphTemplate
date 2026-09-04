/**
 * 그래프 실행 경로.
 *
 * 이 화면에서 가장 중요한 요소입니다. 답변만 보면 어떤 노드를 거쳐 나온 답인지 알 수 없으니,
 * 실제로 실행된 노드를 순서대로 이어 그리고 각 노드가 걸린 시간을 함께 보여줍니다.
 * 응답이 도착하면 노드가 왼쪽부터 차례로 켜집니다.
 */
function formatMs(ms) {
  return ms >= 1000 ? `${(ms / 1000).toFixed(1)}s` : `${ms}ms`
}

export function TracePending() {
  return (
    <div className="trace trace--pending" aria-label="그래프 실행 중">
      <span className="trace__running">그래프 실행 중</span>
      <span className="trace__pulse" aria-hidden="true">
        <i />
        <i />
        <i />
      </span>
    </div>
  )
}

export default function TraceRail({ trace }) {
  if (!trace || trace.length === 0) return null

  return (
    <ol className="trace" aria-label="실행된 노드">
      {trace.map((step, index) => (
        <li
          className="trace__node"
          key={`${step.node}-${index}`}
          style={{ '--i': index }}
        >
          <span className="trace__name">{step.node}</span>
          <span className="trace__ms">{formatMs(step.ms)}</span>
        </li>
      ))}
    </ol>
  )
}
