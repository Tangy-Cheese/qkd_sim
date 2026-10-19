// Number line from 0 to 3 showing where S landed relative to the classical (2) and quantum (2√2) limits
const METER_MAX = 3;
const METER_LEFT = 20;
const METER_RIGHT = 380;

function meterX(value) {
    const clamped = Math.min(Math.max(value, 0), METER_MAX);
    return METER_LEFT + (clamped / METER_MAX) * (METER_RIGHT - METER_LEFT);
}

export default function BellMeter({ S, classical, quantum }) {
    const ticks = [0, 1, 2, 3];

    return (
        <svg className="netmap bellmeter" viewBox="0 0 400 90" role="img" aria-label={`Bell value S = ${S.toFixed(3)}`}>
            <rect className="zone classical" x={meterX(0)} y="30" width={meterX(classical) - meterX(0)} height="16" />
            <rect className="zone quantum" x={meterX(classical)} y="30" width={meterX(quantum) - meterX(classical)} height="16" />

            {ticks.map((t) => (
                <text key={t} x={meterX(t)} y="62">{t}</text>
            ))}

            <line className="limit" x1={meterX(classical)} x2={meterX(classical)} y1="24" y2="52" />
            <text className="limit" x={meterX(classical) - 4} y="16" style={{ textAnchor: "end" }}>classical ≤ 2</text>
            <line className="limit" x1={meterX(quantum)} x2={meterX(quantum)} y1="24" y2="52" />
            <text className="limit" x="396" y="16" style={{ textAnchor: "end" }}>quantum 2√2</text>

            <polygon className="needle" points={`${meterX(S)},48 ${meterX(S) - 7},60 ${meterX(S) + 7},60`} transform="translate(0, 16)" />
            {/* near the right edge the label would be cut off, so it hangs to the left of the needle */}
            <text className="needle" x={S > 2.5 ? meterX(S) + 10 : meterX(S)} y="88" style={{ textAnchor: S > 2.5 ? "end" : "middle" }}>S = {S.toFixed(3)}</text>
        </svg>
    );
}
