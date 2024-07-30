/* eslint-disable no-unused-vars */
import React, { use, useCallback, useContext, useEffect, useMemo, useState } from "react"
import { toast } from "react-toastify"

// Import utilities
import { downloadFile, loadJsonSync, processBatchSettings } from "../../utilities/fileManagementUtils"
import { requestBackend } from "../../utilities/requests"
import ProgressBarRequests from "../generalPurpose/progressBarRequests"

// Workflow imports
import { useEdgesState, useNodesState, useReactFlow } from "reactflow"
import { FlowFunctionsContext } from "../flow/context/flowFunctionsContext"
import WorkflowBase from "../flow/workflowBase"
import { ErrorRequestContext } from "../generalPurpose/errorRequestContext"
import { WorkspaceContext } from "../workspace/workspaceContext"

// Import node types
import ExtractionNode from "./nodesTypes/extractionNode"
import FeaturesNode from "./nodesTypes/featuresNode"
import FilterNode from "./nodesTypes/filterNode"
import SegmentationNode from "./nodesTypes/segmentationNode"
import StandardNode from "./nodesTypes/standardNode"

// Import node parameters
import nodesParams from "../../public/setupVariables/allNodesParams"

// Import buttons
import BtnDiv from "../flow/btnDiv"

// Static functions used in the workflow
import { deepCopy, mergeWithoutDuplicates } from "../../utilities/staticFunctions"

// Useful libraries
import { Button } from "primereact/button"
import { OverlayPanel } from "primereact/overlaypanel"
import { SelectButton } from "primereact/selectbutton"
import { useRef } from "react"

// Static nodes parameters
const staticNodesParams = nodesParams

/**
 * @param {String} id id of the workflow for multiple workflows management
 * @param {Function} changeSidebarType function to change the sidebar type
 * @param {String} workflowType type of the workflow (extraction or features)
 * @returns {JSX.Element} A workflow component as defined in /flow
 *
 * @description
 * Component used to display the workflow of the extraction tab of MEDomicsLab.
 */
const FlowCanvas = ({ workflowType, setWorkflowType }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]) // nodes array, setNodes is used to update the nodes array, onNodesChange is a callback hook that is executed when the nodes array is changed
  const [edges, setEdges, onEdgesChange] = useEdgesState([]) // edges array, setEdges is used to update the edges array, onEdgesChange is a callback hook that is executed when the edges array is changed
  const [reactFlowInstance, setReactFlowInstance] = useState(null) // reactFlowInstance is used to get the reactFlowInstance object important for the reactFlow library
  const [nodeInternalUpdate, setNodeUpdate] = useState({}) // nodeUpdate is used to update a node internal data
  const { setViewport } = useReactFlow() // setViewport is used to update the viewport of the workflow
  const [treeData, setTreeData] = useState({}) // treeData is used to set the data of the tree menu
  const [isProgressUpdating, setIsProgressUpdating] = useState(false) // progress is used to store the progress of the workflow execution
  const [progress, setProgress] = useState({
    now: 0,
    currentLabel: ""
  })
  const { groupNodeId, changeSubFlow, updateNode, setNode2Run, nodeUpdate } = useContext(FlowFunctionsContext)
  const { port } = useContext(WorkspaceContext)
  const { setError, setShowError } = useContext(ErrorRequestContext)
  const pageId = "extractionMEDimage" // pageId is used to identify the page in the backend
  const op = useRef(null)
  const modalities = [{ name: "MR" }, { name: "CT" }, { name: "PET" }]
  const [selectedModalities, setSelectModalities] = useState([])

  /**
   * @param {String} sourceNode id of the group that is active
   * @param {String} TargetNode id of the group that is active
   *
   * @description
   * This function updates the filepath retrieved from the source node in the target node settings
   */
  const UpdateFilePath = (sourceNode, targetNode) => {
    // Check if there are any connections between the source and target nodes
    let SourceTargetConnections = edges.filter(
      (edge) => nodes.find((node) => node.id === edge.source).data.internal.type === sourceNode && nodes.find((node) => node.id === edge.target).data.internal.type === targetNode
    )

    // Update the segmentation node's data with the ROIs from the input node
    SourceTargetConnections.forEach((connection) => {
      let sourNodeId = nodes.find((node) => node.id === connection.source).id
      let targetNodeId = nodes.find((node) => node.id === connection.target).id

      let sourceNode = nodes.find((node) => node.id === sourNodeId)
      let targetNode = nodes.find((node) => node.id === targetNodeId)

      if (targetNode.data.internal.settings === undefined) {
        targetNode.data.internal.settings = {}
      }
      if (sourceNode.data.internal.settings === undefined) {
        sourceNode.data.internal.settings = {}
      }

      // ROIs list
      if ("rois" in sourceNode.data.internal.settings) {
        let inputROIs = sourceNode.data.internal.settings.rois
        if ("rois" in targetNode.data.internal.settings) {
          targetNode.data.internal.settings.rois = inputROIs
        } else {
          targetNode.data.internal.settings["rois"] = inputROIs
        }
      }

      // MEDscan filepath
      let inputScan = sourceNode.data.internal.settings.filepath

      targetNode.data.internal.settings["filepath"] = inputScan

      // Update the segmentation node
      setNodes((prevNodes) =>
        prevNodes.map((node) => {
          if (node.id === targetNodeId) {
            return targetNode
          }
          return node
        })
      )
    })
  }

  // Hook executed upon modification of edges to verify the connections between input and segmentation nodes
  useEffect(() => {
    // Check if there are any connections between an input and segmentation node
    const inputSegmentationConnections = edges.filter(
      (edge) =>
        (nodes.find((node) => node.id === edge.source).data.internal.type === "input" && nodes.find((node) => node.id === edge.target).data.internal.type === "segmentation") ||
        (nodes.find((node) => node.id === edge.source).data.internal.type === "segmentation" && nodes.find((node) => node.id === edge.target).data.internal.type === "inputNode")
    )

    nodes.forEach((node) => {
      if (node.data.internal.type === "segmentation") {
        // If the node is a segmentation node and it is connected to an input node, update the ROIs
        if (inputSegmentationConnections.some((connection) => connection.target === node.id)) {
          let inputNode = nodes.find((node) => node.data.internal.type === "input")
          if (inputNode) {
            let inputROIs = inputNode.data.internal.settings.rois
            node.data.internal.settings.rois = inputROIs
          }
        } else {
          // If the node is a segmentation node and it is not connected to an input node, reset ROIs
          if (Object.keys(node.data.internal.settings.rois).length > 0) {
            node.data.internal.settings.rois = {}
            node.data.internal.settings.rois_data = ""
            node.data.internal.settings.selected_rois = {}
          }
        }

        // Update the node
        updateNode({
          id: node.id,
          updatedData: node.data.internal
        })
      }
    })

    UpdateFilePath("input", "segmentation")
    UpdateFilePath("segmentation", "interpolation")
    UpdateFilePath("segmentation", "re-segmentation")
    UpdateFilePath("segmentation", "filter")
    UpdateFilePath("interpolation", "re-segmentation")
    UpdateFilePath("interpolation", "roi_extraction")
    UpdateFilePath("interpolation", "filter")
    UpdateFilePath("re-segmentation", "filter")
    UpdateFilePath("re-segmentation", "roi_extraction")
    UpdateFilePath("filter", "roi_extraction")
    UpdateFilePath("roi_extraction", "roi_extraction")
    UpdateFilePath("roi_extraction", "discretization")
  }, [edges])

  useEffect(() => {
    // Check if there are any connections between an input and segmentation node
    const inputSegmentationConnections = edges.filter(
      (edge) =>
        (nodes.find((node) => node.id === edge.source).data.internal.type === "input" && nodes.find((node) => node.id === edge.target).data.internal.type === "segmentation") ||
        (nodes.find((node) => node.id === edge.source).data.internal.type === "segmentation" && nodes.find((node) => node.id === edge.target).data.internal.type === "inputNode")
    )
    nodes.forEach((node) => {
      if (node.data.internal.type === "segmentation" && inputSegmentationConnections.some((connection) => connection.target === node.id)) {
        let inputNode = nodes.find((node) => node.data.internal.type === "input")
        if (inputNode) {
          let inputROIs = inputNode.data.internal.settings.rois
          node.data.internal.settings.rois = inputROIs
          setNodes((prevNodes) =>
            prevNodes.map((n) => {
              if (n.id === node.id) {
                return node
              }
              return n
            })
          )
        }
      }
    })
  }, [nodeUpdate])

  // Declare node types using useMemo hook to avoid re-creating component types unnecessarily (memoize output)
  const nodeTypes = useMemo(
    () => ({
      segmentationNode: SegmentationNode,
      standardNode: StandardNode,
      filterNode: FilterNode,
      featuresNode: FeaturesNode,
      extractionNode: ExtractionNode
    }),
    []
  )

  // Executes setTreeData when there is a change in nodes or edges arrays.
  useEffect(() => {
    setTreeData(createTreeFromNodes())
  }, [nodes, edges])

  // Hook executed upon modification of groupNodeId to show the current workflow
  useEffect(() => {
    // If there is a groupNodeId, the workflow is a features workflow
    if (groupNodeId.id != "MAIN") {
      // Set the workflow type to features
      setWorkflowType("features")
      // Hide the nodes that are not in the features group
      hideNodesbut(groupNodeId.id)
    } else {
      // Else the workflow is an extraction workflow
      setWorkflowType("extraction")
      // Hide the nodes that are not in the extraction group
      hideNodesbut(groupNodeId.id)
    }
  }, [groupNodeId])

  // Add warning to extraction node if no features are selected
  useEffect(() => {
    let foundExtractionNode = false
    var nodeExtractionExists = new Object()
    nodes.forEach((node) => {
      nodeExtractionExists = nodes.find((node) => node.data.internal.type === "extraction")
      let possibleFeatures = ["MORPH", "LI", "STATS", "IH", "IVH", "GLCM", "GLDZM", "GLRLM", "GLSZM", "NGLDM", "NGTDM"]
      if (nodeExtractionExists) {
        if (possibleFeatures.includes(node.name)) {
          foundExtractionNode = true
          return
        }
      }
    })
    if (nodeExtractionExists && Object.keys(nodeExtractionExists).length > 0 && !foundExtractionNode) {
      nodeExtractionExists.data.internal.hasWarning = { state: true, tooltip: <p>No features selected! Click on node to select the features to extract.</p> }
    }
  }, [nodes])

  /**
   * @param {String} activeNodeId id of the group that is active
   *
   * @description
   * This function hides the nodes and edges that are not in the active group
   * each node has a subflowId that is the id of the group it belongs to
   * if the subflowId is not equal to the activeNodeId, then the node is hidden
   */
  const hideNodesbut = (activeNodeId) => {
    setNodes((nodes) =>
      nodes.map((node) => {
        node = {
          ...node
        }
        node.hidden = node.data.internal.subflowId != activeNodeId
        return node
      })
    )

    setEdges((edges) =>
      edges.map((edge) => {
        edge = {
          ...edge
        }
        edge.hidden = nodes.find((node) => node.id === edge.source).data.internal.subflowId != activeNodeId || nodes.find((node) => node.id === edge.target).data.internal.subflowId != activeNodeId
        return edge
      })
    )
  }

  /**
   * @returns {Object} updated tree data
   *
   * @description
   * This function creates the tree data from the nodes array
   * it is used to create the recursive workflow
   */
  const createTreeFromNodes = useCallback(() => {
    // Recursively create tree from nodes
    const createTreeFromNodesRec = (node) => {
      let children = {}
      edges.forEach((edge) => {
        if (edge.source == node.id) {
          let targetNode = JSON.parse(JSON.stringify(nodes.find((node) => node.id === edge.target)))
          if (targetNode.type != "extractionNode") {
            let subIdText = ""
            let subflowId = targetNode.data.internal.subflowId
            if (subflowId != "MAIN") {
              console.log("subflowId", subflowId)
              subIdText = JSON.parse(JSON.stringify(nodes.find((node) => node.id == subflowId))).data.internal.name + "."
            }
            children[targetNode.id] = {
              label: subIdText + targetNode.data.internal.name,
              nodes: createTreeFromNodesRec(targetNode)
            }
          }
        }
      })
      return children
    }

    // Create the tree data
    let treeMenuData = {}
    edges.forEach((edge) => {
      let sourceNode = JSON.parse(JSON.stringify(nodes.find((node) => node.id === edge.source)))

      // If the node is an input node, add its tree to the treeMenuData (input node is always a root of a tree)
      if (sourceNode.data.internal.type === "input") {
        treeMenuData[sourceNode.id] = {
          label: sourceNode.data.internal.name,
          nodes: createTreeFromNodesRec(sourceNode)
        }
      }
    })

    return treeMenuData
  }, [nodes, edges])

  /**
   * @param {Object} newNode base node object
   * @param {String} associatedNode id of the parent node if the node is a sub-group node
   * @returns {Object} updated node object
   *
   * @description
   * Function passed to workflowBase to add the specific properties of a
   * node in the workflow for extraction or features
   */
  const addSpecificToNode = (newNode, associatedNode) => {
    newNode.id = `${newNode.id}${associatedNode ? `.${associatedNode}` : ""}`

    // Add defaut parameters of node to possibleSettings
    let type = newNode.data.internal.type.replaceAll(/ |-/g, "_").replace(/[^a-z_]/g, "")

    let setupParams = {}
    if (staticNodesParams[workflowType][type]) {
      setupParams = JSON.parse(JSON.stringify(staticNodesParams[workflowType][type]))
    }

    // Add default parameters to node data
    newNode.data.setupParam = setupParams

    // Initialize settings in node data to put the parameters selected by the user
    let featuresNodeDefaultSettings = { features: ["extract_all"] }
    if (["GLCM", "GLRLM"].includes(newNode.name)) {
      featuresNodeDefaultSettings = {
        features: ["extract_all"],
        dist_correction: "false",
        merge_method: "vol_merge"
      }
    }
    newNode.data.internal.settings = newNode.type === "featuresNode" ? featuresNodeDefaultSettings : newNode.data.setupParam.possibleSettings.defaultSettings

    newNode.data.internal.subflowId = !associatedNode ? groupNodeId.id : associatedNode

    // Used to enable the view button of a node (if it exists)
    newNode.data.internal.enableView = false

    // Add warning to node
    newNode.data.internal.hasWarning = { state: false }

    // Add dictionnary to put results in node data if the node is an extractionNode
    if (newNode.type === "extractionNode") {
      newNode.data.internal.results = {}
    }

    return newNode
  }

  /**
   * @param {Object} id id of the node to delete
   *
   * @description
   * This function is called when the user clicks on the delete button of a node
   * it deletes the node and its edges. If the node is a group node, it deletes
   * all the nodes inside the group node
   */
  const deleteNode = useCallback(
    (id) => {
      console.log("Deleting node ", id)

      setNodes((nds) =>
        nds.reduce((filteredNodes, n) => {
          if (n.id !== id) {
            filteredNodes.push(n)
          }

          if (n.type == "extractionNode") {
            let childrenNodes = nds.filter((node) => node.data.internal.subflowId == id)
            childrenNodes.forEach((node) => {
              deleteNode(node.id)
            })
          }

          return filteredNodes
        }, [])
      )
      setEdges((eds) => eds.filter((e) => e.source !== id && e.target !== id))
    },
    [nodes]
  )

  /**
   * @returns {Object} modified flow instance, if a reactFlowInstance exists
   *
   * @description
   * Temporary fix used to simulate the call to the backend that is not yet refactored
   * Will be removed when the backed is finished
   * TODO : Did not do the special case for extraction node!
   */
  const transformFlowInstance = useCallback(() => {
    // Initialize the new dictionnary for the modified flow
    let modifiedFlow = {
      drawflow: {
        Home: {
          data: {}
        }
      }
    }

    // If the reactFlowInstance exists
    if (reactFlowInstance) {
      let flow = JSON.parse(JSON.stringify(reactFlowInstance.toObject()))
      console.log("The current React Flow instance is : ")
      console.log(flow)

      flow.nodes.forEach((node) => {
        const nodeID = node.id

        // If the node is a features node
        if (node.type === "featuresNode") {
          // If the node is a featuresNode, it has a subflowId and its module name is extraction-subFlowId
          let moduleName = "extraction-" + node.data.internal.subflowId
          // If the subFlowId structure is not already created, create it
          if (!(moduleName in modifiedFlow.drawflow)) {
            modifiedFlow.drawflow[moduleName] = {
              data: {}
            }
          }

          // Add the node data to the subFlowId structure
          modifiedFlow.drawflow[moduleName].data[nodeID] = {
            id: nodeID,
            name: node.data.setupParam.possibleSettings.defaultSettings.MEDimageName,
            data: node.data.internal.settings,
            class: node.className,
            inputs: {},
            outputs: {}
          }
        } else {
          modifiedFlow.drawflow.Home.data[nodeID] = {
            id: nodeID,
            name: node.data.internal.type.replaceAll(/ |-/g, "_"),
            data: node.data.internal.settings ? node.data.internal.settings : {},
            class: node.className,
            inputs: {},
            outputs: {}
          }
        }
      })

      // Note : only the nodes in home module can be connected, therefore it is not necessary to check
      // if the edges to be in the structure other than Home in the dictionnary
      flow.edges.forEach((edge) => {
        const sourceNode = flow.nodes.find((node) => node.id === edge.source)
        const targetNode = flow.nodes.find((node) => node.id === edge.target)

        const sourceNodeID = sourceNode.id
        const targetNodeID = targetNode.id

        const outputKey = "output_1"
        const inputKey = "input_1"

        if (!modifiedFlow.drawflow.Home.data[sourceNodeID].outputs[outputKey]) {
          modifiedFlow.drawflow.Home.data[sourceNodeID].outputs[outputKey] = {
            connections: [{ node: targetNodeID, input: inputKey }]
          }
        } else {
          modifiedFlow.drawflow.Home.data[sourceNodeID].outputs[outputKey].connections.push({ node: targetNodeID, input: inputKey })
        }

        if (!modifiedFlow.drawflow.Home.data[targetNodeID].inputs[inputKey]) {
          modifiedFlow.drawflow.Home.data[targetNodeID].inputs[inputKey] = {
            connections: [{ node: sourceNodeID, output: outputKey }]
          }
        } else {
          modifiedFlow.drawflow.Home.data[targetNodeID].inputs[inputKey].connections.push({ node: sourceNodeID, output: outputKey })
        }
      })

      // Return the modified flow instance that can be sent to the backend
      return modifiedFlow
    }

    return null
  }, [reactFlowInstance])

  /**
   * @param {Object} oldNodeData data of the node before the backend call
   * @param {Object} response response from the backend
   * @returns {Object} new node data
   *
   * @description
   * Handles merge between the already existing data of an extraction node and the response dictionnary from the backend
   * TODO : Should not have to be used after refactoring of backend
   */
  const handleExtractionResults = (oldNodeData, response) => {
    // Get the results that were in the node
    let oldResults = oldNodeData
    let newResults = oldResults
    if (Object.keys(oldResults).length === 0) {
      // If there is no results yet in this node (first run), create a new dictionnary
      for (let file in response) {
        newResults[file] = { RUN_1: {} }
        let pipelineNumber = 1
        for (let pip in response[file]) {
          let newPipelineName = "pipeline " + pipelineNumber
          newResults[file]["RUN_1"][newPipelineName] = response[file][pip]
          newResults[file]["RUN_1"][newPipelineName]["settings"]["fullPipelineName"] = { pip }
          pipelineNumber++
        }
      }
    } else {
      for (let file in response) {
        // Check if the file is alreay in the results
        if (file in oldResults) {
          // Add the new results to the dictionnary
          let runNumber = Object.keys(oldResults[file]).length + 1
          newResults[file]["RUN_" + runNumber] = {}
          let pipelineNumber = 1
          for (let pip in response[file]) {
            let newPipelineName = "pipeline " + pipelineNumber
            newResults[file]["RUN_" + runNumber][newPipelineName] = response[file][pip]
            newResults[file]["RUN_" + runNumber][newPipelineName]["settings"]["fullPipelineName"] = { pip }
            pipelineNumber++
          }
        } else {
          // Create a new dictionnary for the file
          newResults[file] = { RUN_1: {} }
          let pipelineNumber = 1
          for (let pip in response[file]) {
            let newPipelineName = "pipeline " + pipelineNumber
            newResults[file]["RUN_1"][newPipelineName] = response[file][pip]
            newResults[file]["RUN_1"][newPipelineName]["settings"]["fullPipelineName"] = { pip }
            pipelineNumber++
          }
        }
      }
    }
    return newResults
  }

  /**
   * @param {String} id id of the node to execute
   *
   * @description
   * This function is called when the user clicks on the run button of a node
   * It executes the pipelines finishing with this node
   */
  const runNode = useCallback(
    (id) => {
      if (id) {
        console.log("Running node", id)

        // Transform the flow instance to a dictionary compatible with the backend
        let newFlow = transformFlowInstance()
        console.log("Flow dictionary sent to backend is : ", newFlow)

        try {
          // Get the node from id
          let nodeName = newFlow.drawflow.Home.data[id] ? newFlow.drawflow.Home.data[id].name : "extraction"

          // POST request to /extraction_MEDimage/run for the current node by sending form_data
          let formData = {
            id: id,
            name: nodeName,
            // eslint-disable-next-line camelcase
            json_scene: newFlow
          }

          // Activate progress if node is extraction node
          if (nodeName === "extraction") {
            // Start progress bar
            setProgress({now: 0, currentLabel: progress.currentLabel})
            setIsProgressUpdating(true)
          }

          // Activate progress if node is extraction node
          if (nodeName === "extraction") {
            // Start progress bar
            setProgress({now: 0, currentLabel: progress.currentLabel})
            setIsProgressUpdating(true)
          }

          requestBackend(port, "/extraction_MEDimage/run_all/node" + pageId, formData, (response) => {
            if (response.error) {
              // show error message
              toast.error(response.error)
              console.log("error", response.error)

              // check if error has message or not
              if (response.error.message) {
                console.log("error message", response.error.message)
                setError(response.error)
              } else {
                console.log("error no message", response.error)
                setError({ message: response.error })
              }
              setShowError(true)

                // Update progress
                if (nodeName === "extraction") {
                  // Update progress
                  setIsProgressUpdating(false)
                  setProgress({
                    now: 0,
                    currentLabel: ""
                  })
                }
            } else {
              toast.success("Node executed successfully")
              console.log("Response from backend is: ", response)

              // Update node 2 run
              setNode2Run(null)

              // Get all the nodes in the executed pipeline
              let executedNodes = []
              for (let files in response) {
                for (let pipeline in response[files]) {
                  let pipelineNodeIds = pipeline.match(/node_[a-f0-9-]+/g)
                  executedNodes = mergeWithoutDuplicates(executedNodes, pipelineNodeIds)
                }
              }

              // Update progress
              if (nodeName === "extraction") {
                setIsProgressUpdating(false)
                setProgress({
                  now: 100,
                  currentLabel: "Done!"
                })
              }

              // Update the extractionNode data with the response from the backend
              // And enable the view button of the nodes
              setNodes((prevNodes) =>
                prevNodes.map((node) => {
                  if (node.id === id && node.type === "extractionNode") {
                    console.log("Updating node extractionNode runNode", node)
                    // Get the results that were in the node
                    let oldResults = node.data.internal.results
                    let newResults = handleExtractionResults(oldResults, response)

                    return {
                      ...node,
                      data: {
                        ...node.data,
                        internal: {
                          ...node.data.internal,
                          results: newResults // Update the results data with the response
                        }
                      }
                    }
                  }

                  if (executedNodes.includes(node.id)) {
                    // Enable the view button of the node
                    node.data.internal.enableView = true
                    updateNode({
                      id: node.id,
                      updatedData: node.data.internal
                    })
                  }

                  return node
                })
              )
            }
          })
        } catch (error) {
          toast.error("Error running node : ", error)
        }
      }
    },
    [nodes, edges, reactFlowInstance]
  )

  /**
   * @description
   * Runs all the pipelines in the workflow
   */
  const onRun = useCallback(() => {
    console.log("Running workflow")

    // Transform the flow instance to a dictionnary compatible with the backend
    let newFlow = transformFlowInstance()
    console.log("Flow dictionnary sent to back end is : ")
    console.log(newFlow)

    // Start progress bar
    setProgress({ now: 0, currentLabel: progress.currentLabel })
    setIsProgressUpdating(true)

    // Post request to extraction_MEDimage/run_all for current workflow
    requestBackend(port, "/extraction_MEDimage/run_all/" + pageId, newFlow, (response) => {
      if (response.error) {
        // show error message
        toast.error(response.error)
        console.log("error", response.error)

        // Update progress
        setIsProgressUpdating(false)
        setProgress({
          now: 0,
          currentLabel: ""
        })
        setProgress({
          now: 0,
          currentLabel: ""
        })

        // check if error has message or not
        if (response.error.message) {
          console.log("error message", response.error.message)
          setError(response.error)
        } else {
          console.log("error no message", response.error)
          setError({
            message: response.error
          })
        }
        setShowError(true)
      } else {
        console.log("Response from the backend :", response)
        toast.success("Workflow executed successfully")

        // Update progress
        setIsProgressUpdating(false)
        setProgress({
          now: 100,
          currentLabel: "Done!"
        })

        // A response from the backend is only given if there are e
        setNodes((prevNodes) =>
          prevNodes.map((node) => {
            // If the type of the node is extractionNode, update the results according
            // to the response from the backend
            if (node.type === "extractionNode") {
              // Get the results that were in the node
              let oldResults = node.data.internal.results
              let newResults = handleExtractionResults(oldResults, response)

              return {
                ...node,
                data: {
                  ...node.data,
                  internal: {
                    ...node.data.internal,
                    results: newResults // Update the results data with the response
                  }
                }
              }
            }

            // Enable the view button of the node
            node.data.internal.enableView = true
            updateNode({
              id: node.id,
              updatedData: node.data.internal
            })

            return node
          })
        )
      }
    })
  }, [nodes, edges, reactFlowInstance])

  /**
   * @description
   * Clear the canvas if the user confirms
   */
  const onClear = useCallback(() => {
    // Check if the workflow exists and there are nodes in the workflow
    if (reactFlowInstance && nodes.length > 0) {
      let confirmation = confirm("Are you sure you want to clear the canvas?\nEvery data will be lost.")
      if (confirmation) {
        setNodes([])
        setEdges([])
      }
    } else {
      toast.warn("No workflow to clear")
    }
  }, [reactFlowInstance, nodes])

  /**
   * @description
   * Save the workflow as a json file
   */
  const onSave = useCallback(() => {
    if (reactFlowInstance && nodes.length > 0) {
      const flow = JSON.parse(JSON.stringify(reactFlowInstance.toObject()))
      flow.nodes.forEach((node) => {
        node.data.setupParam = null
        // Set enableView to false because only the scene is saved
        // and importing it back would not reload the volumes that
        // were loaded in the viewer
        node.data.enableView = false
      })
      console.log("flow", flow)
      downloadFile(flow, "experiment.json")
    } else {
      // Warn the user if there is no workflow to save
      toast.warn("No workflow to save!")
    }
  }, [reactFlowInstance, nodes])

  /**
   * @description
   * Load a workflow from a json file
   */
  const onLoad = useCallback(() => {
    // Ask confirmation from the user if the canvas is not empty,
    // since the workflow will be replaced
    let confirmation = true
    if (nodes.length > 0) {
      confirmation = confirm("Are you sure you want to import a new experiment?\nEvery data will be lost.")
    }
    if (confirmation) {
      // If the user confirms, load the json file
      const restoreFlow = async () => {
        try {
          // Ask user for the json file to open
          const flow = await loadJsonSync() // wait for the json file to be loaded (see /utilities/fileManagementUtils.js)
          console.log("loaded flow", flow)

          // TODO : should have conditions regarding json file used for import!
          // For each nodes in the json file, add the specific parameters
          Object.values(flow.nodes).forEach((node) => {
            // the line below is important because functions are not serializable
            // set workflow type
            let subworkflowType = node.data.internal.subflowId != "MAIN" ? "extraction" : "features"
            // set node type
            let setupParams = deepCopy(staticNodesParams[subworkflowType][node.name.toLowerCase().replaceAll(" ", "_")])
            node.data.setupParam = setupParams
          })

          if (flow) {
            const { x = 0, y = 0, zoom = 1 } = flow.viewport
            setNodes(flow.nodes || [])
            setEdges(flow.edges || [])
            setViewport({ x, y, zoom })
          }
        } catch (error) {
          toast.warn("Error loading file : ", error)
        }
      }

      // Call the async function
      restoreFlow()
    }
  }, [setNodes, setViewport, nodes])

  /**
   * @description
   * Export the settings of the workflow as a json file for batch extraction
   */
  const onExport = useCallback(() => {
    if (reactFlowInstance && nodes.length > 0) {
      const flow = JSON.parse(JSON.stringify(reactFlowInstance.toObject()))
      flow.nodes.forEach((node) => {
        node.data.setupParam = null
        // Set enableView to false because only the scene is saved
        // and importing it back would not reload the volumes that
        // were loaded in the viewer
        node.data.enableView = false
      })
      processBatchSettings(flow, selectedModalities, "extraction_settings.json")
      //downloadFile(flow, "experiment.json")
    } else {
      // Warn the user if there is no workflow to save
      toast.warn("No workflow to export!")
    }
  }, [reactFlowInstance, nodes])

  /**
   * @description
   * Set the subflow id to null to go back to the main workflow
   */
  const onBack = useCallback(() => {
    changeSubFlow("MAIN")
  }, [])

  // TODO : take out of mandatory in flow/workflowBase.js
  const onNodeDrag = useCallback(
    (event, node) => {
      // TODO
    },
    [nodes]
  )
  /**
   * @param {object} params
   * @param {string} params.source
   * @param {string} params.target
   * @param {string} params.sourceHandle
   * @param {string} params.targetHandle
   *
   * @description
   * This function is called when the user connects two nodes
   * It verifies if a connection is valid for the current workflow
   */
  const isGoodConnection = (connection) => {
    // Getting the source and target nodes
    let sourceNode = nodes.find((node) => node.id == connection.source)
    let targetNode = nodes.find((node) => node.id == connection.target)
    let sourceNodeType = sourceNode.data.internal.type
    let targetNodeType = targetNode.data.internal.type

    // If the connection is between an input and a segmentation node
    if ((sourceNodeType == "input" && targetNodeType == "segmentation") || (sourceNodeType == "segmentation" && targetNodeType == "input")) {
      // If the segmentation node already has an input, a connection to a new input is not allowed
      if (edges.find((edge) => edge.target == targetNode.id)) {
        return false
      }
    }

    return true
  }

  return (
    <>
      <WorkflowBase
        // mandatory props
        mandatoryProps={{
          reactFlowInstance: reactFlowInstance,
          setReactFlowInstance: setReactFlowInstance,
          addSpecificToNode: addSpecificToNode,
          nodeTypes: nodeTypes,
          nodes: nodes,
          setNodes: setNodes,
          onNodesChange: onNodesChange,
          edges: edges,
          setEdges: setEdges,
          onEdgesChange: onEdgesChange,
          onNodeDrag: onNodeDrag,
          runNode: runNode,
          nodeUpdate: nodeInternalUpdate,
          setNodeUpdate: setNodeUpdate
        }}
        // optional props
        onDeleteNode={deleteNode}
        isGoodConnection={isGoodConnection}
        // represents the visual of the workflow

        uiTopRight={
          <>
            {workflowType == "extraction" ? (
              <>
                <BtnDiv
                  key="btnDiv"
                  buttonsList={[
                    { type: "run", onClick: onRun },
                    { type: "clear", onClick: onClear },
                    { type: "save", onClick: onSave },
                    { type: "load", onClick: onLoad },
                    { type: "export", onClick: onExport }
                  ]}
                  op={op}
                />
                <OverlayPanel showCloseIcon ref={op}>
                  <div className="card flex flex-wrap justify-content-center gap-3">
                    <SelectButton value={selectedModalities} onChange={(e) => setSelectModalities(e.value)} optionLabel="name" options={modalities} multiple />
                    <Button onClick={onExport} label="Export" />
                  </div>
                </OverlayPanel>
              </>
            ) : (
              <BtnDiv buttonsList={[{ type: "back", onClick: onBack }]} />
            )}
          </>
        }
        ui={
          <>
            <div className="panel-bottom-center">
              {isProgressUpdating && (
                <ProgressBarRequests
                  progressBarProps={{ animated: true, variant: "success" }}
                  isUpdating={isProgressUpdating}
                  setIsUpdating={setIsProgressUpdating}
                  progress={progress}
                  setProgress={setProgress}
                  requestTopic={"extraction_MEDimage/progress/" + pageId}
                />
              )}
            </div>
          </>
        }
      />
    </>
  )
}

export default FlowCanvas
