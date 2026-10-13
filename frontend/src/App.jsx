import { useState } from 'react'
import TitleScreen from './components/TitleScreen.jsx'
import BB84 from './components/bb84.jsx'
import E91 from './components/e91.jsx'
import './App.css'

function App() {
  let [currentPage, setCurrentPage] = useState("TitleScreen")

  function handleBB84Click(){
    setCurrentPage("bb84")
  } 

  function handleE91Click(){
    setCurrentPage("e91")
  } 

  function handleReturnClick(){
    setCurrentPage("TitleScreen")
  }
  
  return (
    <div id="body">
      {currentPage == "TitleScreen" ? 
        <TitleScreen handleBB84Click={() => handleBB84Click()} handleE91Click={() => handleE91Click()}/> : 
        currentPage == "bb84" ?
          <><BB84 /><button onClick={handleReturnClick}>Back to main page</button></> :
          <E91 handleReturnClick={() => handleReturnClick()}/>
      }
    </div>
  )
}

export default App
