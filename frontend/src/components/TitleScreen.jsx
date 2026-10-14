import { useEffect, useState } from "react";
import { addVisitor, getVisitors } from "../api.js";

const COUNTED_KEY = "qkdsim_counted";

// Count each browser session once. Reloads and coming back to the home page only read the total.
// Kept outside the component so StrictMode mounting twice does not send two visits.
let visitorRequest = null;

function loadVisitors() {
    if (!visitorRequest) {
        let counted = false;
        try {
            counted = sessionStorage.getItem(COUNTED_KEY) === "1";
        } catch {
            // storage blocked, count this page load
        }

        visitorRequest = (counted ? getVisitors() : addVisitor()).then((data) => {
            try {
                sessionStorage.setItem(COUNTED_KEY, "1");
            } catch {
                // nothing to remember it in
            }
            return data.count;
        });
        visitorRequest.catch(() => {
            visitorRequest = null; // try again next time the home page opens
        });
    }
    return visitorRequest;
}

function useVisitorCount() {
    const [count, setCount] = useState(undefined); // undefined while loading, null if the backend is offline

    useEffect(() => {
        let cancelled = false;
        loadVisitors()
            .then((n) => { if (!cancelled) setCount(n); })
            .catch(() => { if (!cancelled) setCount(null); });
        return () => { cancelled = true; };
    }, []);

    return count;
}

export default function TitleScreen(){
    const hits = useVisitorCount();

    return(
        <>
            <h1 id="welcomeMessage">Welcome to QKDSim!</h1>
            <p className="centre">
                You have reached the <b>home page</b> of the quantum key distribution simulator.
                Sign the guestbook... just kidding, there is no guestbook, Eve would read it.
            </p>
            <hr />
            <p id="buttonExplain">Choose which protocol you want to simulate from the following:</p>
            <ul className="links">
                <li>
                    <a href="#bb84">BB84</a> <span className="new blink">HOT!</span><br />
                    Alice, Bob, one fibre and (maybe) an eavesdropper.
                </li>
                <li>
                    <a href="#e91">E91</a><br />
                    Entanglement based key distribution. Still being built!
                </li>
            </ul>
            <p>Or wire up a whole network of nodes:</p>
            <ul className="links">
                <li>
                    <a href="#network">Network Simulation</a> <span className="new blink">NEW!</span><br />
                    Trusted node key relay over the lowest loss route.
                </li>
            </ul>
            <hr />
            <div className="construction" />
            <p className="centre">
                <span className="blink">!!</span> This site is always UNDER CONSTRUCTION <span className="blink">!!</span>
            </p>
            <div className="construction" />
            <p className="centre">
                {hits === undefined ? (
                    "Counting visitors..."
                ) : hits === null ? (
                    "Visitor count unavailable while the backend is offline."
                ) : (
                    <>
                        You are visitor number{" "}
                        <span className="counter">
                            {String(hits).padStart(6, "0").split("").map((digit, i) => <b key={i}>{digit}</b>)}
                        </span>
                    </>
                )}
            </p>
        </>
    )
}
