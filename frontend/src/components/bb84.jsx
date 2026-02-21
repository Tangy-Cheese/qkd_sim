import { useState } from "react";

export default function BB84({ handleReturnClick }) {
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [controller, setController] = useState(null);

    function handleCancelClick(){
        setCancelled(True);
    }

    async function simulateProtocol(e) {
        e.preventDefault();

        const formData = new FormData(e.target);
        const abortController = new AbortController();
        setController(abortController);

        const payload = {
            protocol: "BB84",
            length: Number(formData.get("keylen")),
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
                <div>
                <h2>Simulation Result</h2>
                <p>Error rate: {result.measurements.error_rate}</p>
                </div>
            )}

            <button onClick={handleReturnClick}>Back to main page</button>
        </>
    );
}