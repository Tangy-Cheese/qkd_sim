const HITS_KEY = "qkdsim_hits";

// Counts visits from this browser only, there is no server side counter
function bumpHits() {
    try {
        const hits = Number(localStorage.getItem(HITS_KEY) ?? 1336) + 1;
        localStorage.setItem(HITS_KEY, String(hits));
        return hits;
    } catch {
        return 1337;
    }
}

const hits = bumpHits();

export default function TitleScreen(){
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
            <hr />
            <div className="construction" />
            <p className="centre">
                <span className="blink">!!</span> This site is always UNDER CONSTRUCTION <span className="blink">!!</span>
            </p>
            <div className="construction" />
            <p className="centre">
                You are visitor number{" "}
                <span className="counter">
                    {String(hits).padStart(6, "0").split("").map((digit, i) => <b key={i}>{digit}</b>)}
                </span>
            </p>
        </>
    )
}
