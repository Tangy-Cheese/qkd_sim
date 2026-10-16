import { useEffect, useState } from 'react'
import TitleScreen from './components/TitleScreen.jsx'
import BB84 from './components/bb84.jsx'
import E91 from './components/e91.jsx'
import NetworkMap from './components/networkmap.jsx'
import { getDefaultNetwork } from './api.js'
import './App.css'

const PAGES = [
  { hash: "", label: "Home" },
  { hash: "bb84", label: "BB84" },
  { hash: "e91", label: "E91" },
  { hash: "network", label: "Network" },
]

const STATUS_POLL_MS = 5000

function currentHash() {
  return window.location.hash.replace(/^#/, "")
}

// The page shown follows the URL hash, so the nav is made of real links and the back button works
function useHashPage() {
  const [page, setPage] = useState(currentHash)

  useEffect(() => {
    const onHashChange = () => setPage(currentHash())
    window.addEventListener("hashchange", onHashChange)
    return () => window.removeEventListener("hashchange", onHashChange)
  }, [])

  return page
}

// Pings the backend every few seconds so the sidebar can show whether uvicorn is up
function useBackendStatus() {
  const [status, setStatus] = useState("checking")

  useEffect(() => {
    let cancelled = false

    async function ping() {
      try {
        await getDefaultNetwork()
        if (!cancelled) setStatus("online")
      } catch {
        if (!cancelled) setStatus("offline")
      }
    }

    ping()
    const timer = setInterval(ping, STATUS_POLL_MS)

    return () => {
      cancelled = true
      clearInterval(timer)
    }
  }, [])

  return status
}

function App() {
  const currentPage = useHashPage()
  const status = useBackendStatus()

  return (
    <div id="body">
      <div id="banner">
        <h1 className="rainbow">~* QKDSim *~</h1>
        <p>A simulator for quantum key distribution protocols and networks.</p>
        <div className="marquee">
          <span>
            *** WELCOME TO QKDSIM *** BB84 over lossy fibre, with or without an eavesdropper *** NEW: multi node NETWORK
            simulation with trusted node key relay *** E91 is not implemented yet ***
          </span>
        </div>
      </div>

      <div id="layout">
        <div id="sidebar">
          <h3>Navigation</h3>
          <ul>
            {PAGES.map((page) => (
              <li key={page.hash} className={page.hash === currentPage ? "current" : undefined}>
                <a href={"#" + page.hash}>{page.label}</a>
              </li>
            ))}
          </ul>

          <h3>Server</h3>
          <div id="status">
            {status === "online" && <span className="online">● BACKEND ONLINE</span>}
            {status === "offline" && (
              <>
                <span className="offline blink">● BACKEND OFFLINE</span>
                <small>start uvicorn on port 8000</small>
              </>
            )}
            {status === "checking" && <span className="checking">○ DIALING...</span>}
          </div>
        </div>

        <div id="content">
          {currentPage === "bb84" ?
            <BB84 /> :
            currentPage === "e91" ?
              <E91 /> :
              currentPage === "network" ?
                <NetworkMap /> :
                <TitleScreen />
          }
        </div>
      </div>

      <div id="footer">
        <hr />
        <span className="badge">Frontend: React + Vite</span>
        <span className="badge">Backend: FastAPI + NumPy</span>
        <span className="badge">MIT License</span>
        <p>
          © 2026 QKDSim. Source code on{" "}
          <a href="https://github.com/Tangy-Cheese/qkd_sim">GitHub</a>.
        </p>
      </div>
    </div>
  )
}

export default App
