export default function TitleScreen({ handleBB84Click, handleE91Click }){
    return(
        <>
            <h1 id="welcomeMessage">Welcome to QKDSim!</h1>
            <p id="buttonExplain">Choose which protocol you want to simulate from the following:</p>
            <div className="buttons">
                <button onClick={handleBB84Click}>BB84</button>
                <button onClick={handleE91Click}>E91</button>
            </div>
        </>
    )
}