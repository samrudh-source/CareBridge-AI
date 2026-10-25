import { useState } from 'react'
import {
  Activity,
  ArrowRight,
  Building2,
  CircleAlert,
  FileHeart,
  HeartPulse,
  LoaderCircle,
  MapPin,
  Pill,
  Search,
  ShieldCheck,
  Stethoscope,
} from 'lucide-react'

const API = import.meta.env.VITE_API_BASE_URL || ''

const workflows = [
  {
    id: 'hospital_access',
    title: 'Hospital access',
    desc: 'Departments and official contact pathways',
    icon: Building2,
    placeholder: 'e.g. hospitals with cardiology services nearby',
  },
  {
    id: 'medicine_blood',
    title: 'Medicine & blood',
    desc: 'Licensed blood banks and reliable medicine sources',
    icon: Pill,
    placeholder: 'e.g. O-negative blood near Bengaluru',
  },
  {
    id: 'clinical_trials',
    title: 'Clinical trials',
    desc: 'Registered trials for clinician review',
    icon: FileHeart,
    placeholder: 'e.g. registered trials for a condition near Bengaluru',
  },
  {
    id: 'financial_assistance',
    title: 'Financial assistance',
    desc: 'Official healthcare schemes and requirements',
    icon: ShieldCheck,
    placeholder: 'e.g. government schemes that may support treatment costs',
  },
]

function statusClass(status) {
  if (status?.includes('SYNTHETIC')) return 'status demo'
  if (status?.includes('NOT VERIFIED')) return 'status warning'
  if (status?.includes('LIVE SOURCE LISTING')) return 'status live'
  return 'status neutral'
}

function safeSourceUrl(value) {
  if (!value) return null
  try {
    const url = new URL(value)
    return ['http:', 'https:'].includes(url.protocol) ? url.href : null
  } catch {
    return null
  }
}

function formatTimestamp(value) {
  if (!value) return 'Timestamp unavailable'
  const date = new Date(value)
  return Number.isNaN(date.getTime())
    ? 'Timestamp unavailable'
    : date.toLocaleString()
}

function ResultDetails({ result }) {
  const details = [
    ['Address', result.address],
    ['Phone', result.phone],
    ['Location', result.location],
    ['Recruitment status (source-reported)', result.recruitment_status],
    ['Eligibility (source-reported)', result.eligibility],
    ['Documents (source-reported)', result.documents_required],
  ].filter(([, value]) => value)

  if (!result.provider_name && !result.source_name && details.length === 0) {
    return null
  }

  return (
    <dl className="provider-details">
      {result.provider_name && (
        <div>
          <dt>Provider</dt>
          <dd>{result.provider_name}</dd>
        </div>
      )}
      {result.source_name && (
        <div>
          <dt>Source</dt>
          <dd>{result.source_name}</dd>
        </div>
      )}
      {details.map(([label, value]) => (
        <div key={label}>
          <dt>{label}</dt>
          <dd>{value}</dd>
        </div>
      ))}
    </dl>
  )
}

function ResultCard({ result, index, mode }) {
  const sourceUrl = safeSourceUrl(result.source_url)
  const description = result.description || result.summary

  return (
    <article className="result">
      <div className="resulttop">
        <small>{String(index + 1).padStart(2, '0')}</small>
        <span className={statusClass(result.status)}>{result.status}</span>
      </div>
      <h3>{result.title}</h3>
      {description && <p>{description}</p>}
      <ResultDetails result={result} />
      {sourceUrl && (
        <a
          className="source-link"
          href={sourceUrl}
          target="_blank"
          rel="noopener noreferrer"
        >
          Open source <ArrowRight size={15} aria-hidden="true" />
        </a>
      )}
      <div className="timestamp">
        <Activity size={14} aria-hidden="true" />
        <span>
          {mode === 'live' ? 'Searched ' : 'Demo created '}
          {formatTimestamp(result.checked_at)}
        </span>
        {result.source_date && (
          <span className="source-date">Source date: {result.source_date}</span>
        )}
      </div>
      {mode === 'live' && (
        <span className="status warning verification-status">
          {result.verification_status || 'NOT VERIFIED'}
        </span>
      )}
      {result.next_step && (
        <div className="next">
          <Stethoscope size={16} aria-hidden="true" />
          <span>
            <b>Recommended next action</b>
            {result.next_step}
          </span>
        </div>
      )}
    </article>
  )
}

export default function App() {
  const [workflow, setWorkflow] = useState('hospital_access')
  const [query, setQuery] = useState('')
  const [location, setLocation] = useState('Bengaluru')
  const [mode, setMode] = useState('demo')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [response, setResponse] = useState(null)
  const selected = workflows.find((item) => item.id === workflow)

  async function search() {
    const searchQuery = query.trim()
    if (searchQuery.length < 3) {
      setError('Describe what you need to find using at least 3 characters.')
      setResponse(null)
      return
    }

    setLoading(true)
    setError('')
    setResponse(null)

    try {
      const result = await fetch(`${API}/api/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          workflow,
          query: searchQuery,
          location: location.trim() || 'Bengaluru',
          mode,
        }),
      })
      const data = await result.json()

      if (!result.ok) {
        const detail = data.detail
        const message =
          typeof detail === 'string'
            ? detail
            : detail?.message || 'The search could not be completed.'
        setError(
          mode === 'live'
            ? `Live search failed: ${message}`
            : `Demo search failed: ${message}`,
        )
        return
      }

      setResponse(data)
    } catch {
      setError(
        'Could not reach or read the API response. Check that the backend is running, then retry.',
      )
    } finally {
      setLoading(false)
    }
  }

  function submit(event) {
    event.preventDefault()
    search()
  }

  function changeWorkflow(id) {
    setWorkflow(id)
    setResponse(null)
    setError('')
  }

  function changeMode(nextMode) {
    setMode(nextMode)
    setResponse(null)
    setError('')
  }

  return (
    <div className="shell">
      <header className="topbar">
        <a className="brand" href="/" aria-label="CareBridge AI home">
          <span className="brandmark">
            <HeartPulse aria-hidden="true" />
          </span>
          CareBridge <b>AI</b>
        </a>
        <div className="topmeta">
          <span>TINYFISH SEARCH</span>
          <b>TEAM DUALITH</b>
        </div>
      </header>

      <section className="hero">
        <div>
          <p className="eyebrow">HEALTHCARE INFORMATION NAVIGATION</p>
          <h1>
            One patient.
            <br />
            <em>One journey.</em>
            <br />
            Connected care.
          </h1>
          <p className="sub">
            Coordinate healthcare-information discovery across selected
            sources, with visible evidence, honest uncertainty and a clear next
            step.
          </p>
          <div className="tags">
            <span>✓ Source-aware workflow</span>
            <span>✓ Human confirmation</span>
          </div>
        </div>
        <div className="visual" aria-hidden="true">
          <div className="orbit one" />
          <div className="orbit two" />
          <div className="core">
            <HeartPulse size={42} />
            <b>CARE JOURNEY</b>
          </div>
          <i className="node n1"><Building2 /></i>
          <i className="node n2"><Pill /></i>
          <i className="node n3"><FileHeart /></i>
          <i className="node n4"><ShieldCheck /></i>
        </div>
      </section>

      <div className="notice" role="note">
        <CircleAlert aria-hidden="true" />
        <p>
          <b>Important:</b> Demo mode contains fictional synthetic examples.
          Live mode searches real TinyFish source listings, but listings are
          <b> not independently verified</b>. Neither mode guarantees
          appointments, blood or medicine stock, clinical-trial eligibility, or
          scheme approval. Do not use this service for urgent care or enter
          sensitive patient information.
        </p>
      </div>

      <main>
        <div className="sectionhead">
          <div>
            <p className="eyebrow">DISCOVERY WORKSPACE</p>
            <h2>What do you need help finding?</h2>
            <p className="muted">
              Choose one workflow and describe the information you need.
            </p>
          </div>
          <div className="mode" aria-label="Search mode">
            <small>MODE</small>
            <button
              type="button"
              className={mode === 'demo' ? 'chosen' : ''}
              aria-pressed={mode === 'demo'}
              disabled={loading}
              onClick={() => changeMode('demo')}
            >
              Synthetic demo
            </button>
            <button
              type="button"
              className={mode === 'live' ? 'chosen' : ''}
              aria-pressed={mode === 'live'}
              disabled={loading}
              onClick={() => changeMode('live')}
            >
              Live sources
            </button>
          </div>
        </div>

        <div className="workflows" aria-label="Healthcare workflows">
          {workflows.map((item) => {
            const Icon = item.icon
            return (
              <button
                type="button"
                key={item.id}
                className={`workflow ${workflow === item.id ? 'active' : ''}`}
                aria-pressed={workflow === item.id}
                disabled={loading}
                onClick={() => changeWorkflow(item.id)}
              >
                <span className="wicon"><Icon aria-hidden="true" /></span>
                <span>
                  <b>{item.title}</b>
                  <small>{item.desc}</small>
                </span>
                <ArrowRight className="arrow" aria-hidden="true" />
              </button>
            )
          })}
        </div>

        <form className="searchform" onSubmit={submit} aria-busy={loading}>
          <div className="formtitle">
            <span>01</span>
            <div>
              <b>{selected.title}</b>
              <small>
                {mode === 'live'
                  ? 'Search source listings using the selected workflow'
                  : 'Run fictional examples clearly marked as synthetic'}
              </small>
            </div>
          </div>
          <label htmlFor="query">Your request</label>
          <div className="query">
            <Search aria-hidden="true" />
            <input
              id="query"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder={selected.placeholder}
              minLength={3}
              maxLength={500}
              disabled={loading}
            />
          </div>
          <div className="formbottom">
            <label className="loc" htmlFor="location">
              <span><MapPin size={15} aria-hidden="true" /> Location</span>
              <input
                id="location"
                value={location}
                onChange={(event) => setLocation(event.target.value)}
                maxLength={120}
                disabled={loading}
              />
            </label>
            <button className="submit" type="submit" disabled={loading}>
              {loading ? (
                <>
                  <LoaderCircle className="spinner" size={17} aria-hidden="true" />
                  Searching…
                </>
              ) : mode === 'demo' ? (
                <>Run synthetic demo <ArrowRight size={17} aria-hidden="true" /></>
              ) : (
                <>Search live sources <ArrowRight size={17} aria-hidden="true" /></>
              )}
            </button>
          </div>
          {error && (
            <div className="error-panel" role="alert">
              <p>{error}</p>
              <button type="button" onClick={search} disabled={loading}>
                Retry search
              </button>
            </div>
          )}
        </form>

        {response && (
          <section className="results" aria-live="polite">
            <div className="resulthead">
              <div>
                <p className="eyebrow">
                  {response.mode === 'live' ? 'LIVE SEARCH' : 'SYNTHETIC DEMO'}
                  {' / '}
                  {selected.title.toUpperCase()}
                </p>
                <h2>Discovery summary</h2>
              </div>
              <span className={statusClass(response.overall_status)}>
                {response.overall_status}
              </span>
            </div>
            <p className="muted">{response.message}</p>
            <p className="result-count">
              {response.results.length}{' '}
              {response.results.length === 1 ? 'result' : 'results'}
            </p>
            {response.results.length > 0 ? (
              <div className="resultgrid">
                {response.results.map((result, index) => (
                  <ResultCard
                    key={`${result.source_url || result.title}-${index}`}
                    result={result}
                    index={index}
                    mode={response.mode}
                  />
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <Search aria-hidden="true" />
                <h3>No source listings found</h3>
                <p>
                  {response.mode === 'live'
                    ? 'Try a broader request or location. No source-backed findings are available for this search.'
                    : 'There are no demo examples for this request.'}
                </p>
                <button type="button" onClick={search} disabled={loading}>
                  Retry search
                </button>
              </div>
            )}
            <div className="safety">
              <ShieldCheck size={17} aria-hidden="true" />
              {response.safety_notice}
            </div>
          </section>
        )}

        <section className="principles">
          <div>
            <b>01 / Discover</b>
            <h3>Selected sources</h3>
            <p>Prioritize official and workflow-relevant information sources.</p>
          </div>
          <div>
            <b>02 / Verify</b>
            <h3>Honest status</h3>
            <p>Separate synthetic demo data from source listings and unknowns.</p>
          </div>
          <div>
            <b>03 / Act with care</b>
            <h3>Human confirmation</h3>
            <p>Providers and qualified professionals confirm details and decisions.</p>
          </div>
        </section>
      </main>

      <footer>
        <span>CareBridge AI · DUALITH</span>
        <span>Samrudh N. · Khyati Agarwal</span>
        <span>Swim with Tiny Fish</span>
      </footer>
    </div>
  )
}
