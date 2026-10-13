// Grey box with a title bar, used to frame forms and results
export default function Window({ title, children }) {
    return (
        <div className="window">
            <div className="window-title">
                <span>{title}</span>
                <span className="window-buttons" aria-hidden="true">
                    <b>_</b><b>□</b><b>×</b>
                </span>
            </div>
            <div className="window-body">
                {children}
            </div>
        </div>
    );
}
