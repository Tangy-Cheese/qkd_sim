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
                    <a href="#e91">E91</a> <span className="new blink">NEW!</span><br />
                    Entangled photon pairs and a Bell test to catch Eve.
                </li>
            </ul>
            <p>Or wire up a whole network of nodes:</p>
            <ul className="links">
                <li>
                    <a href="#network">Network Simulation</a> <span className="new blink">NEW!</span><br />
                    Trusted node key relay over the lowest loss route.
                </li>
            </ul>
        </>
    )
}
