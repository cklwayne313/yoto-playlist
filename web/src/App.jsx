import { useCallback, useEffect, useMemo, useState } from 'react'
import data from './data/playlists.json'

const { stats, playlists } = data
const BASE = import.meta.env.BASE_URL

const VERDICTS = [['all', 'All cards'], ['CORE', 'Core cards'], ['GOOD', 'Good cards'], ['FUN', 'Fun cards'], ['LATER', 'Later cards']]
const LANGS = [['all', 'All languages'], ['cantonese', 'Cantonese'], ['english', 'English']]
const COVERS = [['all', 'All covers'], ['official', 'Yoto art'], ['custom', 'Made here']]
const SERIES = [['all', 'All series'], ['kafoo', '嘉芙姐姐'], ['zeongogo', '志安哥哥'], ['sunshine', '天晴童謠'],
  ['super-simple', 'Super Simple'], ['disney', 'Disney'], ['therapy', 'Speech therapy'], ['other', 'Other']]
const SPEECH = [['all', 'Any speech score'], ['5', 'Best for talking'], ['4', 'Good for talking']]

const shortName = (p) => p.name.split(' — ')[0]

function readHash() {
  const raw = (window.location.hash || '').replace(/^#/, '') || '/'
  const [path, qs] = raw.split('?')
  return { path: path || '/', params: Object.fromEntries(new URLSearchParams(qs || '')) }
}

function buildHash(path, params) {
  const sp = new URLSearchParams()
  for (const [k, v] of Object.entries(params)) {
    if (v && v !== 'all' && !(k === 'sort' && v === 'rank')) sp.set(k, v)
  }
  const qs = sp.toString()
  return '#' + path + (qs ? '?' + qs : '')
}

function useHashRoute() {
  const [route, setRoute] = useState(readHash)
  useEffect(() => {
    const onHash = () => setRoute(readHash())
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])
  const go = useCallback((path, params, replace = false) => {
    const url = buildHash(path, params)
    if (replace) {
      window.history.replaceState(null, '', url)
      setRoute(readHash())
    } else {
      window.location.hash = url
    }
  }, [])
  return [route, go]
}

function Stars({ n, max = 5 }) {
  return (
    <span className="stars" aria-label={`${n} of ${max}`}>
      {'★'.repeat(n)}<span className="starsOff">{'★'.repeat(max - n)}</span>
    </span>
  )
}

function Select({ label, options, value, onChange }) {
  return (
    <span className="selectWrap">
      <select className="select" aria-label={label} value={value}
        onChange={e => onChange(e.target.value)}>
        {options.map(([v, text]) => <option key={v} value={v}>{text}</option>)}
      </select>
    </span>
  )
}

function Card({ p }) {
  const facts = [p.tracks + (p.tracks === 1 ? ' song' : ' songs'), p.runtime].filter(Boolean)
  return (
    <a className="card" href={`#/p/${p.folder}`}>
      <img className="cardCover" src={`${BASE}covers/${p.folder}.jpg`} alt=""
        loading="lazy" decoding="async" width="400" height="634" />
      <div className="cardText">
        <p className="cardLine">{p.rank} · {p.kicker}</p>
        <h2 className="cardTitle">{shortName(p)}</h2>
        <p className="cardFacts">
          {facts.join(' · ')}
          {(p.verdict === 'CORE' || p.verdict === 'LATER') &&
            <span className={'verdict ' + p.verdict}>{p.verdict}</span>}
        </p>
      </div>
    </a>
  )
}

function Detail({ p, onBack }) {
  return (
    <main className="detail">
      <button className="back" type="button" onClick={onBack}>← All cards</button>
      <div className="detailHead">
        <img className="detailCover" src={`${BASE}covers/full/${p.folder}.jpg`} alt={`${shortName(p)} cover`} />
        <div>
          <p className="detailLine">{p.kicker}</p>
          <h1 className="detailTitle">{shortName(p)}</h1>
          {p.name !== shortName(p) && <p className="detailSub">{p.name.split(' — ').slice(1).join(' — ')}</p>}
          <p className="detailMeta">
            Rank {p.rank} of {stats.count} · {p.tracks} songs{p.runtime ? ` · ${p.runtime}` : ''}
          </p>
          <p className="detailScores">
            <span>Speech <Stars n={p.speech} /></span>
            <span>Age 2 <Stars n={p.age} /></span>
          </p>
        </div>
      </div>
      <p className="why">{p.why}</p>
      <article className="prose" dangerouslySetInnerHTML={{ __html: p.body }} />
    </main>
  )
}

export default function App() {
  const [route, go] = useHashRoute()
  const [open, setOpen] = useState(false)

  const { path, params } = route
  const q = params.q || ''
  const filters = {
    verdict: params.v || 'all',
    lang: params.lang || 'all',
    cover: params.cover || 'all',
    series: params.series || 'all',
    speech: params.speech || 'all',
  }
  const sort = params.sort || 'rank'

  const set = (patch, replace = true) => go(path, { ...params, ...patch }, replace)

  const shown = useMemo(() => {
    const needle = q.trim().toLowerCase()
    const list = playlists.filter(p => {
      if (filters.verdict !== 'all' && p.verdict !== filters.verdict) return false
      if (filters.lang !== 'all' && p.lang !== filters.lang) return false
      if (filters.cover !== 'all' && p.cover !== filters.cover) return false
      if (filters.series !== 'all' && p.series !== filters.series) return false
      if (filters.speech === '5' && p.speech !== 5) return false
      if (filters.speech === '4' && p.speech < 4) return false
      if (needle) {
        const hay = (p.name + ' ' + p.kicker + ' ' + p.why).toLowerCase()
        if (!hay.includes(needle)) return false
      }
      return true
    })
    if (sort === 'name') list.sort((a, b) => shortName(a).localeCompare(shortName(b), 'zh-Hant'))
    if (sort === 'speech') list.sort((a, b) => b.speech - a.speech || a.rank - b.rank)
    if (sort === 'rank') list.sort((a, b) => a.rank - b.rank)
    return list
  }, [q, filters.verdict, filters.lang, filters.cover, filters.series, filters.speech, sort])

  const activeCount = Object.values(filters).filter(v => v !== 'all').length
  const detail = path.startsWith('/p/') ? playlists.find(p => p.folder === path.slice(3)) : null

  const onBack = () => {
    if (window.history.length > 1) window.history.back()
    else window.location.hash = '#/'
  }

  const pickRandom = () => {
    const pool = shown.length ? shown : playlists
    const p = pool[Math.floor(Math.random() * pool.length)]
    window.location.hash = `#/p/${p.folder}`
  }

  if (detail) {
    return (
      <div className="app">
        <Detail p={detail} onBack={onBack} />
        <footer className="foot">
          <span>Art belongs to its owners · built from RANKING.md</span>
          <a href={`${BASE}covers-sheet.jpg`}>All covers</a>
        </footer>
      </div>
    )
  }

  return (
    <div className="app">
      <div className="intro">
        <div className="introTop">
          <a className="wordmark" href="#/">Him<span>Him</span></a>
          <div className="tools">
            <button className="tool" type="button" onClick={pickRandom}>Pick one</button>
          </div>
        </div>
        <div className="introGrid">
          <div>
            <h1>{stats.count} cards,<br />for one two-year-old.</h1>
            <p className="lede">
              Cantonese first, then English — ordered by what helps him talk, not by what looks good on a shelf.
            </p>
          </div>
          <p className="aside">
            {stats.songs} songs · {stats.runtime}
            <br />
            <a href={`${BASE}covers-sheet.jpg`}>Every cover on one page</a>
          </p>
        </div>
      </div>

      <header className="masthead">
        <div className="searchRow">
          <label className="srOnly" htmlFor="q">Search cards</label>
          <input className="search" id="q" type="search" value={q} enterKeyHint="search"
            placeholder="Search a card by name" aria-label="Search cards"
            onChange={e => set({ q: e.target.value })} />
        </div>

        <div className="controls">
          <Select label="Language" options={LANGS} value={filters.lang} onChange={v => set({ lang: v })} />
          <Select label="Series" options={SERIES} value={filters.series} onChange={v => set({ series: v })} />
          <Select label="Order" options={[['rank', 'Best first'], ['name', 'A–Z'], ['speech', 'Talking first']]}
            value={sort} onChange={v => set({ sort: v })} />
          <button className="moreBtn" type="button" onClick={() => setOpen(o => !o)} aria-expanded={open}>
            {open ? 'Fewer filters' : 'More filters'}
          </button>
        </div>

        {open && (
          <div className="morePanel">
            <Select label="Show" options={VERDICTS} value={filters.verdict} onChange={v => set({ v })} />
            <Select label="Cover" options={COVERS} value={filters.cover} onChange={v => set({ cover: v })} />
            <Select label="For talking" options={SPEECH} value={filters.speech} onChange={v => set({ speech: v })} />
          </div>
        )}

        {(activeCount > 0 || q) && (
          <div className="statusLine">
            <span className="counting">{shown.length} of {stats.count} cards</span>
            <button className="clearBtn" type="button" onClick={() => go('/', {}, true)}>Clear</button>
          </div>
        )}
      </header>

      <main className="shelf" aria-live="polite">
        {shown.map(p => <Card key={p.folder} p={p} />)}
      </main>

      {!shown.length && (
        <p className="empty">
          No card matches that. <button className="linkBtn" type="button" onClick={() => go('/', {}, true)}>Show all {stats.count}</button>
        </p>
      )}

      <footer className="foot">
        <span>{stats.songs} songs · {stats.runtime} · art belongs to its owners</span>
        <a href={`${BASE}covers-sheet.jpg`}>Every cover on one page</a>
      </footer>
    </div>
  )
}
