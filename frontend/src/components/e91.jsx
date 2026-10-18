import { useRef, useState } from "react";
import { runE91 } from "../api.js";
import Window from "./Window.jsx";

const KEY_PREVIEW_BITS = 96;

function keyPreview(key) {
    if (!key) {
        return "(empty)";
    }
    return key.length > KEY_PREVIEW_BITS ? key.slice(0, KEY_PREVIEW_BITS) + "..." : key;
}

// Number line from 0 to 3 showing where S landed relative to the classical (2) and quantum (2√2) limits
const METER_MAX = 3;
const METER_LEFT = 20;
const METER_RIGHT = 380;

function meterX(value) {
    const clamped = Math.min(Math.max(value, 0), METER_MAX);
    return METER_LEFT + (clamped / METER_MAX) * (METER_RIGHT - METER_LEFT);
}

function BellMeter({ S, classical, quantum }) {
    const ticks = [0, 1, 2, 3];

    return (
        <svg className="netmap bellmeter" viewBox="0 0 400 90" role="img" aria-label={`Bell value S = ${S.toFixed(3)}`}>
            <rect className="zone classical" x={meterX(0)} y="30" width={meterX(classical) - meterX(0)} height="16" />
            <rect className="zone quantum" x={meterX(classical)} y="30" width={meterX(quantum) - meterX(classical)} height="16" />

            {ticks.map((t) => (
                <text key={t} x={meterX(t)} y="62">{t}</text>
            ))}

            <line className="limit" x1={meterX(classical)} x2={meterX(classical)} y1="24" y2="52" />
            <text className="limit" x={meterX(classical) - 4} y="16" textAnchor="end">classical ≤ 2</text>
            <line className="limit" x1={meterX(quantum)} x2={meterX(quantum)} y1="24" y2="52" />
            <text className="limit" x="396" y="16" textAnchor="end">quantum 2√2</text>

            <polygon className="needle" points={`${meterX(S)},48 ${meterX(S) - 7},60 ${meterX(S) + 7},60`} transform="translate(0, 16)" />
            <text className="needle" x={meterX(S)} y="88">S = {S.toFixed(3)}</text>
        </svg>
    );
}

export default function E91() {
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
            key_length: Number(formData.get("pairs")),
            fibre_length: Number(formData.get("fibrelen")),
            fibre_attenuation: Number(formData.get("fibreatt")),
            eve: formData.get("eve") !== null,
        };

        setLoading(true);
        setError(null);

        try {
            const data = await runE91(payload, controller.current.signal);
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

    const bell = result?.bell_test;

    return (
        <>
            <h1 className="rainbow">E91 Simulation</h1>
            <p>
                A source next to Alice makes pairs of <b>entangled photons</b>. Alice keeps one, the other
                flies down the fibre to Bob. Each measures at a random angle. Matching angles give the
                key, and a <b>Bell test</b> on some of the others proves the photons were still entangled.
                If Eve measured them, the entanglement is gone and the Bell value S falls to 2 or below.
            </p>

            <pre className="ascii">
{eve
? `  ALICE  <~~ [SOURCE] ~~~~>  [ EVE ]  ~~~~>  BOB
  0° 22.5° 45°   |Ψ⁻⟩         o_o  !!    22.5° 45° 67.5°`
: `  ALICE  <~~ [SOURCE] ~~~~~~~~~~~~~~~~~~~~>  BOB
  0° 22.5° 45°   |Ψ⁻⟩    (quantum channel)  22.5° 45° 67.5°`}
            </pre>

            <Window title="e91.exe - Parameters">
                <form onSubmit={simulateProtocol} id="e91Form">
                    <table className="form">
                        <tbody>
                            <tr>
                                <td><label htmlFor="pairs">Entangled pairs:</label></td>
                                <td><input type="number" id="pairs" name="pairs" min="1" max="20000" step="1" defaultValue="20000" required /></td>
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
                            <button type="submit">Simulate E91</button>
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
                <Window title="e91.exe - Bell Test">
                    <p className={bell.violated ? "verdict good" : "verdict bad"}>
                        {bell.violated
                            ? <>*** BELL INEQUALITY VIOLATED *** The photons were entangled.</>
                            : <><span className="blink">*** NO VIOLATION ***</span> Someone broke the entanglement!</>}
                    </p>
                    <BellMeter S={bell.S} classical={bell.classical_bound} quantum={bell.quantum_bound} />
                    <table className="data compact">
                        <thead>
                            <tr><th>Alice</th><th>Bob</th><th>E(a, b)</th><th>Ideal</th><th>Pairs</th></tr>
                        </thead>
                        <tbody>
                            {bell.correlations.map((c) => (
                                <tr key={`${c.alice_angle}-${c.bob_angle}`}>
                                    <td>{c.alice_angle}°</td>
                                    <td>{c.bob_angle}°</td>
                                    <td>{c.correlation.toFixed(3)}</td>
                                    <td>{(-Math.cos(2 * (c.alice_angle - c.bob_angle) * Math.PI / 180)).toFixed(3)}</td>
                                    <td>{c.pairs}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    <p>S = E(0°, 22.5°) − E(0°, 67.5°) + E(45°, 22.5°) + E(45°, 67.5°)</p>
                </Window>
            )}

            {result && (
                <Window title="e91.exe - Simulation Result">
                    <p className={result.aborted ? "verdict bad" : "verdict good"}>
                        {result.aborted
                            ? <><span className="blink">*** ABORTED ***</span> No secure key could be made.</>
                            : <>*** SECURE KEY ESTABLISHED ***</>}
                    </p>
                    <table className="data">
                        <tbody>
                            <tr><th>Protocol</th><td>{result.protocol}</td></tr>
                            <tr><th>Pairs sent</th><td>{result.key_length}</td></tr>
                            <tr><th>Fibre length</th><td>{result.parameters.distance_km} km</td></tr>
                            <tr><th>Fibre attenuation</th><td>{result.parameters.fibre_attenuation} dB/km</td></tr>
                            <tr><th>Dark count rate</th><td>{result.parameters.dark_count_rate}</td></tr>
                            <tr><th>Error rate (QBER)</th><td>{(result.measurements.error_rate * 100).toFixed(2)} %</td></tr>
                            <tr><th>Secure key rate</th><td>{result.measurements.secure_key_rate.toFixed(4)} bits per pair</td></tr>
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
