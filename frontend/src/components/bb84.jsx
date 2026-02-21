import { useState } from 'react'

export default function BB84({ handleReturnClick }){
    function simulateProtocol(formData){
        const keylen = formData.get('keylen')
        const eavesdropper = formData.get('eve') != null ? true: false
        
    }
    
    return(
        <>
            <form action={simulateProtocol} id="bb84Form">
                <div id="bb84FormElement">
                    <label for="keylen">Key length:</label>
                    <input type="text" id="keylen" name="keylen"/>
                </div>
                <div id="bb84FormElement">
                    <label for="eve">Include eavesdropper?</label>
                    <input type="checkbox" id="eve" name="eve"/>
                </div>
                <button type="submit">Simulate BB84</button>
            </form>
            <button onClick={handleReturnClick}>Back to main page</button>
        </>
    )
}