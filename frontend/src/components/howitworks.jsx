import "katex/dist/katex.min.css";
import Theory from "../content/howitworks.mdx";

// The page text lives in src/content/howitworks.mdx: Markdown with LaTeX maths ($...$ and $$...$$)
// and React components such as <Window> and <BellMeter> dropped in between
export default function HowItWorks() {
    return (
        <>
            <h1 className="rainbow">How it works</h1>
            <div className="theory">
                <Theory />
            </div>
            <p className="centre"><a href="#">Back to main page</a></p>
        </>
    );
}
