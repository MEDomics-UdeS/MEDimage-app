import { Card } from "primereact/card"
import { useMemo } from "react"
import { Stack } from "react-bootstrap"
import nodesParams from "../../public/setupVariables/allNodesParams"


/**
 *
 * @param {*} event Represents the drag event that is fired when a node is dragged from the sidebar
 * @param {*} node Information about the node that is being dragged
 *
 * @description
 * This function is called when a node is dragged from the sidebar.
 * It sets the data that is being dragged.
 *
 * @returns {void}
 */
const onDragStart = (event, node) => {
  const stringNode = JSON.stringify(node)
  event.dataTransfer.setData("application/reactflow", stringNode)
  event.dataTransfer.effectAllowed = "move"
}

const SectionContainer = ({ title, children }) => (
  <div className="card mb-3" style={{backgroundColor: "#dbecf9"}}>
    <h6 className="section-header p-2 border-bottom">
      {title}
    </h6>
    <Stack direction="vertical" gap={1}>
      {children}
    </Stack>
  </div>
)

/**
 * @param {string} title The title of the sidebar
 * @param {string} sidebarType Corresponding to a key in nodesParams
 *
 * @returns {JSX.Element} A Card for each node in nodesParams[sidebarType]
 *
 * @description
 * This component is used to display the nodes available in the sidebar.
 *
 */
const SidebarAvailableNodes = ({ title, sidebarType }) => {
  const { initializationNodes, trainingNodes, otherNodes } = useMemo(() => {
    const originalNodes = nodesParams[sidebarType] || {}
    const filteredNodes = Object.fromEntries(
      Object.entries(originalNodes).filter(([, node]) => 
        node?.section !== 'Machine Learning' && node?.section !== 'initialization' && node?.section !== 'analysis'
      )
    )

    // Categorize nodes
    return Object.entries(originalNodes).reduce((acc, [nodeName, node]) => {
      const section = node?.section?.toLowerCase() || 'other'
      if (section.includes('init')) acc.initializationNodes[nodeName] = node
      else if (section.includes('machine')) acc.trainingNodes[nodeName] = node
      else acc.otherNodes[nodeName] = node
      return acc
    }, { 
      initializationNodes: {}, 
      trainingNodes: {}, 
      otherNodes: filteredNodes 
    })
  }, [sidebarType])

  const renderNode = (nodeName, node) => (
    <div
      key={nodeName}
      className="draggable-component"
      onDragStart={(event) =>
        onDragStart(event, {
          nodeType: node.type,
          name: node.title,
          image: node.img
        })
      }
      draggable
    >
      <Card
        className="draggable-side-node"
        pt={{
          body: { className: "padding-0-important" },
          header: { className: "header" }
        }}
        header={
          <>
            {node.title}
            <img 
              src={`/icon/${sidebarType}/${node.img}`} 
              alt={node.title} 
              className="icon-nodes" 
            />
          </>
        }
      />
    </div>
  )

  return (
    <div className="available-nodes-panel-container">
      <Card
        className="text-center height-100 available-nodes-panel"
        title={title}
        pt={{
          body: { className: "overflow-auto height-100 p-2" }
        }}
      >
          {Object.keys(initializationNodes).length > 0 && (
            <SectionContainer title="Initialization Nodes">
              {Object.entries(initializationNodes).map(([nodeName, node]) => 
                renderNode(nodeName, node)
              )}
            </SectionContainer>
          )}

          {Object.keys(trainingNodes).length > 0 && (
            <SectionContainer title="Training Nodes">
              {Object.entries(trainingNodes).map(([nodeName, node]) => 
                renderNode(nodeName, node)
              )}
            </SectionContainer>
          )}


          {Object.keys(otherNodes).length > 0 && (
            <SectionContainer title="Other Nodes">
              {Object.entries(otherNodes).map(([nodeName, node]) => 
                renderNode(nodeName, node)
              )}
            </SectionContainer>
          )}
      </Card>
    </div>
  )
}

export default SidebarAvailableNodes
