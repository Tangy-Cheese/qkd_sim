import { useState } from "react";
import { runE91 } from "../api.js";
import Window from "./Window.jsx";

export default function E91(){
    const [reply, setReply] = useState(null);
    const [loading, setLoading] = useState(false);

    // The backend answers 501 until protocols/e91.py is written, so show whatever it says
    async function askServer() {
        setLoading(true);

        try {
            await runE91({ key_length: 1000, fibre_length: 20, fibre_attenuation: 200, eve: false });
            setReply("The server ran E91! Time to build this page.");
        } catch (err) {
            setReply(err.status ? `HTTP ${err.status}: ${err.message}` : err.message);
        } finally {
            setLoading(false);
        }
    }

    return(
        <>
            <h1 className="rainbow">E91 Simulation</h1>
            <div className="construction" />
            <h2><span className="blink">UNDER CONSTRUCTION</span></h2>
            <div className="construction" />
            <p className="centre">Nothing to see here... (yet)</p>
            <p>
                E91 hands Alice and Bob one half each of an entangled photon pair and uses a Bell test
                to catch eavesdroppers. The backend does not simulate it yet, check back soon!
            </p>

            <Window title="e91.exe">
                <p>Not convinced? Ask the server yourself:</p>
                <div className="buttons">
                    <button onClick={askServer} disabled={loading}>{loading ? "Asking..." : "Run E91 anyway"}</button>
                </div>
                {reply && <p className="error">{reply}</p>}
            </Window>

            <p className="centre"><a href="#">Back to main page</a></p>
        </>
    )
}
