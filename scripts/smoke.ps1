param([string]$BaseUrl = 'http://127.0.0.1:3000')
$ErrorActionPreference = 'Stop'
# Exercise persistence and retrieval, then delete only the document created by this check.
Invoke-RestMethod "$BaseUrl/api/ready" | Out-Null
$payload = @{title='Smoke test'; source_label='smoke-test'; text=('Document retrieval stores source evidence and returns matching excerpts with citations. ' * 5)} | ConvertTo-Json
$document = Invoke-RestMethod "$BaseUrl/api/documents/ingest-text" -Method Post -ContentType 'application/json' -Body $payload
try {
    $answer = Invoke-RestMethod "$BaseUrl/api/query" -Method Post -ContentType 'application/json' -Body '{"question":"How does document retrieval return evidence?"}'
    if ($answer.citations.Count -lt 1) { throw 'No citations returned.' }
    if (-not ($answer.citations.source_label -contains 'smoke-test')) { throw 'Smoke test source was not retrieved.' }
    Write-Output 'Readiness, ingestion, retrieval, and citations passed.'
} finally {
    Invoke-RestMethod "$BaseUrl/api/documents/$($document.id)" -Method Delete | Out-Null
}
