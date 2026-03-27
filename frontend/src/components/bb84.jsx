import { useState } from "react";

export default function BB84({ handleReturnClick }) {
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [controller, setController] = useState(null);

    async function simulateProtocol(e) {
        e.preventDefault();

        const formData = new FormData(e.target);
        const abortController = new AbortController();
        setController(abortController);

        const payload = {
            protocol: "BB84",
            key_length: Number(formData.get("keylen")),
            fibre_length: Number(formData.get("fibrelen")),
            fibre_attenuation: Number(formData.get("fibreatt")),
            eve: formData.get("eve") !== null,
        };

        setLoading(true);

        try {
            const response = await fetch("http://localhost:8000/simulation", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
                signal: abortController.signal
            });
            const data = await response.json();
            setResult(data);
        } catch (err) {
            if (err.name === "AbortError") {
                console.log("Fetch aborted by user");
            } else {
                console.error("Simulation failed:", err);
            }
        } finally {
            setLoading(false);
        }
    }

    return (
        <>

            <h1>BB84 Simulation</h1>

            <form onSubmit={simulateProtocol} id="bb84Form">
                <div id="bb84FormElement">
                    <label htmlFor="keylen">Key length:</label>
                    <input type="number" id="keylen" name="keylen" required />
                </div>
                <div id="bb84FormElement">
                    <label htmlFor="fibrelen">Fibre length (km):</label>
                    <input type="number" id="fibrelen" name="fibrelen" required />
                </div>
                <div id="bb84FormElement">
                    <label htmlFor="fibreatt">Fibre attenuation (e-3):</label>
                    <input type="number" id="fibreatt" name="fibreatt" required />
                </div>
                <div id="bb84FormElement">
                    <label htmlFor="eve">Include eavesdropper?</label>
                    <input type="checkbox" id="eve" name="eve" />
                </div>
                {loading ?
                    <div className="buttons">
                        <button type="submit" disabled={loading}>Running...</button>
                        <button onClick={() => controller?.abort()}>Cancel</button>
                    </div>
                : 
                    <button type="submit" disabled={loading}>Simulate BB84</button>
                }
            </form>

            {result && (
                <div id="results_wrapper">
                    <h2>Simulation Result</h2>
                    <div id="results">
                        <ul>
                            <li>Key length: {result.key_length}</li>
                            <li>Fibre length: {result.parameters.distance_km}km</li>
                            <li>Fibre attenuation: {result.parameters.fibre_attenuation}</li>
                        </ul>
                        <ul>
                            <li>Error rate: {result.measurements.error_rate}</li>
                            <li>Secure key rate: {result.measurements.secure_key_rate}</li>
                            <li>Shared key length: {result.measurements.shared_key_length} qubits</li>
                        </ul>
                    </div>
                </div>
            )}

            <button onClick={handleReturnClick}>Back to main page</button>
        </>
    );
}