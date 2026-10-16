import { useEffect, useRef, useState } from "react";
import { getDefaultNetwork, runSimulation } from "../api.js";
import Window from "./Window.jsx";

const MAP_WIDTH = 520;
const MAP_HEIGHT = 300;
const PARALLEL_GAP = 44;

// Used if the backend cannot be reached when the page loads, same as GET /network/default
const FALLBACK_NETWORK = {
    nodes: ["Alice", "Bob", "Charlie"],
    edges: [
        { node1: "Alice", node2: "Bob", distance_km: 80, attenuation: 0.2, eve: false },
        { node1: "Bob", node2: "Charlie", distance_km: 60, attenuation: 0.2, eve: false },
    ],
};

let nextEdgeId = 0;

function withIds(edges) {
    return edges.map((edge) => ({ ...edge, id: nextEdgeId++ }));
}

// Nodes are spread around an ellipse, starting from the left
function nodePositions(nodes) {
    const positions = {};

    nodes.forEach((name, i) => {
        const angle = Math.PI + (2 * Math.PI * i) / nodes.length;
        positions[name] = {
            x: MAP_WIDTH / 2 + (MAP_WIDTH / 2 - 70) * Math.cos(angle),
            y: MAP_HEIGHT / 2 + (MAP_HEIGHT / 2 - 50) * Math.sin(angle),
        };
    });

    return positions;
}

function pairKey(a, b) {
    return [a, b].sort().join("\u0000");
}

function NetworkSvg({ nodes, edges, root, target, result }) {
    const positions = nodePositions(nodes);
    const usedLinks = new Map((result?.network.links ?? []).map((link) => [pairKey(link.from, link.to), link]));

    return (
        <svg className="netmap" viewBox={`0 0 ${MAP_WIDTH} ${MAP_HEIGHT}`} role="img" aria-label="Network map">
            {edges.map((edge) => {
                const a = positions[edge.node1];
                const b = positions[edge.node2];
                if (!a || !b || edge.node1 === edge.node2) {
                    return null;
                }

                //The backend uses the lowest loss link between two nodes, so only that one is drawn as used
                const link = usedLinks.get(pairKey(edge.node1, edge.node2));
                const loss = (e) => e.distance_km * e.attenuation;
                const used = link && !edges.some((other) =>
                    other.id !== edge.id
                    && pairKey(other.node1, other.node2) === pairKey(edge.node1, edge.node2)
                    && (loss(other) < loss(edge) || (loss(other) === loss(edge) && other.id < edge.id))
                );

                //Links joining the same two nodes are bowed apart so they do not sit on top of each other
                const siblings = edges.filter((other) => pairKey(other.node1, other.node2) === pairKey(edge.node1, edge.node2));
                const bow = (siblings.indexOf(edge) - (siblings.length - 1) / 2) * PARALLEL_GAP;
                const [p, q] = edge.node1 < edge.node2 ? [a, b] : [b, a];
                const length = Math.hypot(q.x - p.x, q.y - p.y) || 1;
                const normalX = -(q.y - p.y) / length;
                const normalY = (q.x - p.x) / length;
                const midX = (a.x + b.x) / 2 + normalX * bow;
                const midY = (a.y + b.y) / 2 + normalY * bow;
                const controlX = (a.x + b.x) / 2 + normalX * bow * 2;
                const controlY = (a.y + b.y) / 2 + normalY * bow * 2;

                return (
                    <g key={edge.id} className={(used ? "edge used" : "edge") + (edge.eve ? " eve" : "")}>
                        <path d={`M ${a.x} ${a.y} Q ${controlX} ${controlY} ${b.x} ${b.y}`} />
                        <text x={midX} y={midY - 6}>
                            {edge.distance_km} km{edge.eve ? " [EVE]" : ""}
                        </text>
                        {used && (
                            <text x={midX} y={midY + 14} className="qber">
                                QBER {(link.qber * 100).toFixed(1)}%
                            </text>
                        )}
                    </g>
                );
            })}

            {nodes.map((name) => {
                const { x, y } = positions[name];
                const role = name === root ? "TX" : name === target ? "RX" : null;

                return (
                    <g key={name} className={role ? "node endpoint" : "node"}>
                        <rect x={x - 14} y={y - 11} width="28" height="22" />
                        <text x={x} y={y + 4} className="role">{role ?? "o"}</text>
                        <text x={x} y={y + 28}>{name}</text>
                    </g>
                );
            })}
        </svg>
    );
}

export default function NetworkMap() {
    const [nodes, setNodes] = useState([]);
    const [edges, setEdges] = useState([]);
    const [root, setRoot] = useState("");
    const [target, setTarget] = useState("");
    const [newNode, setNewNode] = useState("");
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [notice, setNotice] = useState(null);
    const [loading, setLoading] = useState(false);
    const controller = useRef(null);

    // Bumped by the reset button to download the default network again
    const [reloads, setReloads] = useState(0);

    useEffect(() => {
        const abortController = new AbortController();

        function loadNetwork(network) {
            setNodes(network.nodes);
            setEdges(withIds(network.edges));
            setRoot(network.nodes[0] ?? "");
            setTarget(network.nodes[network.nodes.length - 1] ?? "");
            setResult(null);
            setError(null);
        }

        async function fetchDefault() {
            try {
                loadNetwork(await getDefaultNetwork(abortController.signal));
                setNotice(null);
            } catch (err) {
                if (err.name === "AbortError") {
                    return;
                }
                loadNetwork(FALLBACK_NETWORK);
                setNotice(`Could not download the default network (${err.message}) Using a built in copy.`);
            }
        }

        fetchDefault();
        return () => abortController.abort();
    }, [reloads]);

    // Old results describe the old network, so any edit throws them away
    function clearResult() {
        setResult(null);
        setError(null);
    }

    function addNode(e) {
        e.preventDefault();
        const name = newNode.trim();

        if (!name || nodes.includes(name)) {
            return;
        }

        setNodes([...nodes, name]);
        setNewNode("");
        if (!root) setRoot(name);
        else if (!target) setTarget(name);
        clearResult();
    }

    function removeNode(name) {
        const remaining = nodes.filter((node) => node !== name);

        setNodes(remaining);
        setEdges(edges.filter((edge) => edge.node1 !== name && edge.node2 !== name));
        if (root === name) setRoot(remaining[0] ?? "");
        if (target === name) setTarget(remaining[remaining.length - 1] ?? "");
        clearResult();
    }

    function addEdge() {
        setEdges([...edges, ...withIds([{
            node1: nodes[0],
            node2: nodes[1] ?? nodes[0],
            distance_km: 50,
            attenuation: 0.2,
            eve: false,
        }])]);
        clearResult();
    }

    function updateEdge(id, field, value) {
        setEdges(edges.map((edge) => edge.id === id ? { ...edge, [field]: value } : edge));
        clearResult();
    }

    function removeEdge(id) {
        setEdges(edges.filter((edge) => edge.id !== id));
        clearResult();
    }

    async function simulateNetwork(e) {
        e.preventDefault();

        const formData = new FormData(e.target);
        controller.current = new AbortController();

        const payload = {
            nodes,
            edges: edges.map((edge) => ({
                node1: edge.node1,
                node2: edge.node2,
                distance_km: Number(edge.distance_km),
                attenuation: Number(edge.attenuation),
                eve: edge.eve,
            })),
            root,
            target,
            key_length: Number(formData.get("keylen")),
            dark_count_rate: Number(formData.get("darkcount")),
        };

        setLoading(true);
        setError(null);

        try {
            const data = await runSimulation(payload, controller.current.signal);
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

    const nodeOptions = nodes.map((name) => <option key={name} value={name}>{name}</option>);
    const established = result && result.security.final_key_length > 0;

    return (
        <>
            <h1 className="rainbow">Network Simulation</h1>
            <p>
                Build a network of <b>trusted nodes</b> joined by fibres. The server finds the lowest loss
                route from the sender to the receiver, runs BB84 over every link on it and relays the key
                hop by hop. Put Eve on a link and watch the whole route fall over!
            </p>

            {notice && <p className="notice"><span className="blink">!!</span> {notice}</p>}

            <NetworkSvg nodes={nodes} edges={edges} root={root} target={target} result={result} />

            <Window title="network.exe - Nodes">
                <table className="data">
                    <tbody>
                        {nodes.map((name) => (
                            <tr key={name}>
                                <td>{name}</td>
                                <td><button type="button" className="small" onClick={() => removeNode(name)}>Delete</button></td>
                            </tr>
                        ))}
                        {nodes.length === 0 && <tr><td>(no nodes)</td></tr>}
                    </tbody>
                </table>
                <form onSubmit={addNode} className="buttons">
                    <input type="text" value={newNode} onChange={(e) => setNewNode(e.target.value)} placeholder="Node name" maxLength="12" size="14" aria-label="New node name" />
                    <button type="submit" disabled={!newNode.trim() || nodes.includes(newNode.trim())}>Add node</button>
                    <button type="button" onClick={() => setReloads(reloads + 1)}>Reset to default</button>
                </form>
            </Window>

            <Window title="network.exe - Fibre links">
                <table className="data compact">
                    <thead>
                        <tr>
                            <th>From</th>
                            <th>To</th>
                            <th>Length (km)</th>
                            <th>Loss (dB/km)</th>
                            <th>Eve?</th>
                            <th></th>
                        </tr>
                    </thead>
                    <tbody>
                        {edges.map((edge) => (
                            <tr key={edge.id}>
                                <td>
                                    <select value={edge.node1} onChange={(e) => updateEdge(edge.id, "node1", e.target.value)} aria-label="From node">
                                        {nodeOptions}
                                    </select>
                                </td>
                                <td>
                                    <select value={edge.node2} onChange={(e) => updateEdge(edge.id, "node2", e.target.value)} aria-label="To node">
                                        {nodeOptions}
                                    </select>
                                </td>
                                <td><input type="number" min="0" step="any" className="narrow" value={edge.distance_km} onChange={(e) => updateEdge(edge.id, "distance_km", e.target.value)} aria-label="Length in km" /></td>
                                <td><input type="number" min="0" step="any" className="narrow" value={edge.attenuation} onChange={(e) => updateEdge(edge.id, "attenuation", e.target.value)} aria-label="Attenuation in dB per km" /></td>
                                <td><input type="checkbox" checked={edge.eve} onChange={(e) => updateEdge(edge.id, "eve", e.target.checked)} aria-label="Eavesdropper on this link" /></td>
                                <td><button type="button" className="small" onClick={() => removeEdge(edge.id)}>Delete</button></td>
                            </tr>
                        ))}
                        {edges.length === 0 && <tr><td colSpan="6">(no links)</td></tr>}
                    </tbody>
                </table>
                <div className="buttons">
                    <button type="button" onClick={addEdge} disabled={nodes.length < 2}>Add link</button>
                </div>
            </Window>

            <Window title="network.exe - Run">
                <form onSubmit={simulateNetwork}>
                    <table className="form">
                        <tbody>
                            <tr>
                                <td><label htmlFor="netroot">Sender (TX):</label></td>
                                <td><select id="netroot" value={root} onChange={(e) => { setRoot(e.target.value); clearResult(); }}>{nodeOptions}</select></td>
                            </tr>
                            <tr>
                                <td><label htmlFor="nettarget">Receiver (RX):</label></td>
                                <td><select id="nettarget" value={target} onChange={(e) => { setTarget(e.target.value); clearResult(); }}>{nodeOptions}</select></td>
                            </tr>
                            <tr>
                                <td><label htmlFor="netkeylen">Key length (qubits per link):</label></td>
                                <td><input type="number" id="netkeylen" name="keylen" min="1" max="20000" step="1" defaultValue="10000" required /></td>
                            </tr>
                            <tr>
                                <td><label htmlFor="darkcount">Dark count rate:</label></td>
                                <td><input type="number" id="darkcount" name="darkcount" min="0" max="1" step="any" defaultValue="0.001" required /></td>
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
                            <button type="submit" disabled={nodes.length < 2}>Simulate network</button>
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
                <Window title="network.exe - Simulation Result">
                    <p className={established ? "verdict good" : "verdict bad"}>
                        {established
                            ? <>*** SECURE KEY ESTABLISHED ***</>
                            : <><span className="blink">*** ABORTED ***</span> A link on the route produced no secure key.</>}
                    </p>
                    <table className="data">
                        <tbody>
                            <tr>
                                <th>Route</th>
                                <td>{[result.root, ...result.network.links.map((link) => link.to)].join(" -> ")}</td>
                            </tr>
                            <tr><th>Total distance</th><td>{result.network.distance_km} km</td></tr>
                            <tr><th>Trusted relay nodes</th><td>{result.network.number_of_secure_nodes}</td></tr>
                            <tr><th>Worst error rate (QBER)</th><td>{(result.security.qubit_error_rate * 100).toFixed(2)} %</td></tr>
                            <tr><th>Secure key rate (slowest link)</th><td>{result.security.secure_key_rate.toFixed(4)} bits per qubit sent</td></tr>
                            <tr><th>Final key length</th><td>{result.security.final_key_length} bits</td></tr>
                        </tbody>
                    </table>

                    <h3>Per link</h3>
                    <table className="data">
                        <thead>
                            <tr>
                                <th>From</th>
                                <th>To</th>
                                <th>Length</th>
                                <th>QBER</th>
                                <th>Secure key rate</th>
                            </tr>
                        </thead>
                        <tbody>
                            {result.network.links.map((link) => (
                                <tr key={link.from + "\u0000" + link.to}>
                                    <td>{link.from}</td>
                                    <td>{link.to}</td>
                                    <td>{link.distance_km} km</td>
                                    <td>{(link.qber * 100).toFixed(2)} %</td>
                                    <td>{link.skr.toFixed(4)}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </Window>
            )}

            <p className="centre"><a href="#">Back to main page</a></p>
        </>
    );
}
