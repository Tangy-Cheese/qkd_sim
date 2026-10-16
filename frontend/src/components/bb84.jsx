import { useRef, useState } from "react";
import { runBB84 } from "../api.js";
import Window from "./Window.jsx";

const KEY_PREVIEW_BITS = 96;

function keyPreview(key) {
    if (!key) {
        return "(empty)";
    }
    return key.length > KEY_PREVIEW_BITS ? key.slice(0, KEY_PREVIEW_BITS) + "..." : key;
}

export default function BB84() {
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [eve, setEve] = useState(false);
    const controller = useRef(null);

    async function simulateProtocol(e) {
        e.preventDefault();

        const formData = new FormData(e.target);
        controller.current = new AbortController();

        const payload = {
            key_length: Number(formData.get("keylen")),
            fibre_length: Number(formData.get("fibrelen")),
            fibre_attenuation: Number(formData.get("fibreatt")),
            eve: formData.get("eve") !== null,
        };

        setLoading(true);
        setError(null);

        try {
            const data = await runBB84(payload, controller.current.signal);
            setResult(data);
        } catch (err) {
            if (err.name === "AbortError") {
                console.log("Fetch aborted by user");
            } else {
                console.error("Simulation failed:", err);
                setResult(null);
                setError(err.message);
            }
        } finally {
            setLoading(false);
        }
    }

    return (
        <>
            <h1 className="rainbow">BB84 Simulation</h1>
            <p>
                Alice beams polarised photons down a fibre to Bob. They compare bases, throw away the
                mismatches and squeeze a <b>secret key</b> out of what is left. If Eve listens in, the
                error rate gives her away!
            </p>

            <pre className="ascii">
{eve
? `  ALICE  ~~~~~~>  [ EVE ]  ~~~~~~>  BOB
  |0> |+>         o_o  !!           ???`
: `  ALICE  ~~~~~~~~~~~~~~~~~~~~~~~~>  BOB
  |0> |+>     (quantum channel)     ???`}
            </pre>

            <Window title="bb84.exe - Parameters">
                <form onSubmit={simulateProtocol} id="bb84Form">
                    <table className="form">
                        <tbody>
                            <tr>
                                <td><label htmlFor="keylen">Key length (qubits):</label></td>
                                <td><input type="number" id="keylen" name="keylen" min="1" max="20000" step="1" defaultValue="10000" required /></td>
                            </tr>
                            <tr>
                                <td><label htmlFor="fibrelen">Fibre length (km):</label></td>
                                <td><input type="number" id="fibrelen" name="fibrelen" min="0" step="any" defaultValue="20" required /></td>
                            </tr>
                            <tr>
                                <td><label htmlFor="fibreatt">Fibre attenuation (e-3 dB/km):</label></td>
                                <td><input type="number" id="fibreatt" name="fibreatt" min="0" step="any" defaultValue="200" required /></td>
                            </tr>
                            <tr>
                                <td><label htmlFor="eve">Include eavesdropper?</label></td>
                                <td><input type="checkbox" id="eve" name="eve" checked={eve} onChange={(e) => setEve(e.target.checked)} /></td>
                            </tr>
                        </tbody>
                    </table>
                    {loading ?
                        <div className="buttons">
                            <button type="submit" disabled={loading}>Running...</button>
                            <button type="button" onClick={() => controller.current?.abort()}>Cancel</button>
                        </div>
                    :
                        <div className="buttons">
                            <button type="submit">Simulate BB84</button>
                        </div>
                    }
                </form>
            </Window>

            {error && (
                <Window title="Error">
                    <p className="error"><span className="blink">!!</span> {error}</p>
                </Window>
            )}

            {result && (
                <Window title="bb84.exe - Simulation Result">
                    <p className={result.aborted ? "verdict bad" : "verdict good"}>
                        {result.aborted
                            ? <><span className="blink">*** ABORTED ***</span> No secure key could be made.</>
                            : <>*** SECURE KEY ESTABLISHED ***</>}
                    </p>
                    <table className="data">
                        <tbody>
                            <tr><th>Protocol</th><td>{result.protocol}</td></tr>
                            <tr><th>Qubits sent</th><td>{result.key_length}</td></tr>
                            <tr><th>Fibre length</th><td>{result.parameters.distance_km} km</td></tr>
                            <tr><th>Fibre attenuation</th><td>{result.parameters.fibre_attenuation} dB/km</td></tr>
                            <tr><th>Dark count rate</th><td>{result.parameters.dark_count_rate}</td></tr>
                            <tr><th>Error rate (QBER)</th><td>{(result.measurements.error_rate * 100).toFixed(2)} %</td></tr>
                            <tr><th>Secure key rate</th><td>{result.measurements.secure_key_rate.toFixed(4)} bits per qubit sent</td></tr>
                            <tr><th>Sifted key length</th><td>{result.measurements.shared_key_length} bits</td></tr>
                            <tr><th>Secure key length</th><td>{result.measurements.secure_key_length} bits</td></tr>
                            <tr><th>Secure key</th><td><tt className="key">{keyPreview(result.keys.secure_key)}</tt></td></tr>
                        </tbody>
                    </table>
                </Window>
            )}

            <p className="centre"><a href="#">Back to main page</a></p>
        </>
    );
}
