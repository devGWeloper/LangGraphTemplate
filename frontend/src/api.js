export async function fetchTeams() {
  const res = await fetch('/api/teams')
  if (!res.ok) throw new Error('조 목록을 불러오지 못했습니다')
  const body = await res.json()
  return body.teams
}

export async function sendChat(teamId, message, history) {
  const res = await fetch(`/api/chat/${teamId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, history }),
  })
  if (res.status === 404) throw new Error('존재하지 않는 조입니다')
  if (!res.ok) throw new Error('서버에 연결하지 못했습니다')
  return await res.json()
}
