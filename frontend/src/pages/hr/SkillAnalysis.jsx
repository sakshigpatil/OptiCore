import React, { useState } from 'react'
import skillService from '../../services/skillService'

function parseSkills(text) {
  if (!text) return []
  return text.split(/[;,\n]+/).map(s => s.trim()).filter(Boolean)
}

export default function SkillAnalysis() {
  const [employeeName, setEmployeeName] = useState('')
  const [role, setRole] = useState('')
  const [skillsText, setSkillsText] = useState('')
  const [requiredText, setRequiredText] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setResult(null)
    const payload = {
      employee: {
        name: employeeName || 'Unknown',
        role: role || 'Unknown',
        skills: parseSkills(skillsText)
      },
      required_skills: parseSkills(requiredText)
    }

    try {
      const res = await skillService.analyze(payload)
      setResult(res)
    } catch (err) {
      console.error(err)
      setResult({ error: err?.response?.data || String(err) })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold mb-4">Employee Skill Analysis</h2>

      <form onSubmit={submit} className="space-y-4 max-w-2xl">
        <div>
          <label className="block text-sm font-medium">Employee Name</label>
          <input value={employeeName} onChange={e => setEmployeeName(e.target.value)} className="mt-1 block w-full border rounded px-3 py-2" />
        </div>

        <div>
          <label className="block text-sm font-medium">Role</label>
          <input value={role} onChange={e => setRole(e.target.value)} className="mt-1 block w-full border rounded px-3 py-2" />
        </div>

        <div>
          <label className="block text-sm font-medium">Employee Skills (comma/newline separated)</label>
          <textarea value={skillsText} onChange={e => setSkillsText(e.target.value)} rows={3} className="mt-1 block w-full border rounded px-3 py-2" />
        </div>

        <div>
          <label className="block text-sm font-medium">Required Skills (comma/newline separated)</label>
          <textarea value={requiredText} onChange={e => setRequiredText(e.target.value)} rows={3} className="mt-1 block w-full border rounded px-3 py-2" />
        </div>

        <div>
          <button disabled={loading} className="px-4 py-2 bg-blue-600 text-white rounded">{loading ? 'Analyzing...' : 'Analyze'}</button>
        </div>
      </form>

      {result && (
        <div className="mt-6 max-w-2xl">
          {result.error ? (
            <div className="text-red-600">Error: {JSON.stringify(result.error)}</div>
          ) : (
            <div className="space-y-3">
              <div><strong>Employee:</strong> {result.employee}</div>
              <div><strong>Role:</strong> {result.role}</div>
              <div><strong>Skill Match %:</strong> {result.skill_match_percent}%</div>
              <div><strong>TF-IDF Match %:</strong> {result.tfidf_match_percent}%</div>
              <div><strong>Matched Skills:</strong> {result.matched_skills && result.matched_skills.length ? result.matched_skills.join(', ') : 'None'}</div>
              <div><strong>Missing Skills:</strong> {result.missing_skills && result.missing_skills.length ? result.missing_skills.join(', ') : 'None'}</div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
