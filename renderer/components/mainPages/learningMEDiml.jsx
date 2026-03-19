import React, { useState } from "react"
import FlowPageBase from "../flow/flowPageBase"
import ModulePage from "./moduleBasics/modulePage"
import FlowCanvas from "../learningMEDiml/flowCanvas"

// Extraction tab referred to in pages/_app.js.
// Shows sideBar nodes in a div on the left of the page,
// then react flow canvas where the nodes can be dropped.
const LearningMEDimlPage = ({ pageId, configPath = "" }) => {

  // Hook for current module
  const [flowType, setFlowType] = useState("learningMEDiml") // this state has been implemented because of subflows implementation

  return (
    <>
      <ModulePage pageId={pageId} configPath={configPath}>
        <FlowPageBase workflowType={flowType} id={pageId} LearningMEDiml={true}>
          <FlowCanvas id={pageId} workflowType={flowType} setWorkflowType={setFlowType} />
        </FlowPageBase>
      </ModulePage>
    </>
  )
}

export default LearningMEDimlPage
