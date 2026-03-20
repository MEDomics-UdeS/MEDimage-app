import { createContext, useContext, useState } from "react"
import { toast } from "react-toastify"
import { WorkspaceContext } from "../../workspace/workspaceContext"
import { FlowInfosContext } from "./flowInfosContext"

// This context is used to store the flowResults (id and type of the workflow)
const FlowResultsContext = createContext()

/**
 *
 * @param {*} children components that will use the context
 * @description This component is used to provide the flowResults context to all the components that need it.
 */
function FlowResultsProvider({ children }) {
  const [flowResults, setFlowResults] = useState({}) // Initial style
  const [showResultsPane, setShowResultsPane] = useState(false) // Initial state
  const [isResults, setIsResults] = useState(false) // Initial state
  const [selectedResultsId, setSelectedResultsId] = useState(null) // Initial state

  // This function is used to update the flowResults
  const updateFlowResults = async (newResults, sceneFolderId) => {
    if (!newResults) return
    const isValidFormat = (results) => {
      if (results?.nodes) {
        return results.nodes.some(node => {
          if (node.type === "Analyze") {
            return !!node.data?.internal?.results
          }
          return false
        })
      }
      return false
    }
    if (isValidFormat(newResults)) {
      setIsResults(true)
    } else {
      console.error("Could not update flow results: Invalid format or not available.")
    }
  }

  return (
    // in the value attribute we pass the flowResults and the function to update it.
    // These will be available to all the components that use this context
    <FlowResultsContext.Provider
      value={{
        flowResults,
        updateFlowResults,
        showResultsPane,
        setShowResultsPane,
        isResults,
        setIsResults,
        selectedResultsId,
        setSelectedResultsId
      }}
    >
      {children}
    </FlowResultsContext.Provider>
  )
}

export { FlowResultsContext, FlowResultsProvider }

