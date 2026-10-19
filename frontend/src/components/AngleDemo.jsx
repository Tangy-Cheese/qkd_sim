import { useState } from "react";

// Slider for the angle between Alice's and Bob's polarisers, showing how often an entangled pair
// gives opposite results and the correlation E that goes into the Bell test
export default function AngleDemo() {
    const [delta, setDelta] = useState(22.5);

    const rad = delta * Math.PI / 180;
    const opposite = Math.cos(rad) ** 2;
    const same = 1 - opposite;
    const E = same - opposite;

    return (
        <div className="angledemo">
            <label htmlFor="angledemo">Angle between polarisers: <b>{delta.toFixed(1)}°</b></label>
            <input
                type="range"
                id="angledemo"
                min="0"
                max="90"
                step="0.5"
                value={delta}
                onChange={(e) => setDelta(Number(e.target.value))}
            />
            <table className="data compact">
                <tbody>
                    <tr>
                        <th>Opposite results, cos²Δ</th>
                        <td><span className="bar opposite" style={{ width: `${opposite * 100}%` }} /></td>
                        <td>{(opposite * 100).toFixed(1)} %</td>
                    </tr>
                    <tr>
                        <th>Same results, sin²Δ</th>
                        <td><span className="bar same" style={{ width: `${same * 100}%` }} /></td>
                        <td>{(same * 100).toFixed(1)} %</td>
                    </tr>
                    <tr>
                        <th>Correlation E = −cos 2Δ</th>
                        <td colSpan="2">{E.toFixed(3)}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    );
}
