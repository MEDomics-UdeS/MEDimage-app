import { Dropdown } from "primereact/dropdown"
import { InputSwitch } from 'primereact/inputswitch'
import { InputText } from 'primereact/inputtext'
import { useContext, useEffect, useState } from "react"
import { Col, Form, Row } from "react-bootstrap"
import DocLink from "../../extractionMEDiml/docLink"
import Node, { updateHasWarning } from "../../flow/node"
import { DataContext } from "../../workspace/dataContext"
import { set } from "lodash"

/**
 * @param {string} id id of the node
 * @param {object} data data of the node
 * @param {string} type type of the node
 * @returns {JSX.Element} A SegmentationNode node
 *
 * @description
 * This component is used to display a SegmentationNode node.
 * it handles the display of the node and the modal
 */
const Split = ({ id, data, type }) => { 
  const [selectedCSVFile, setSelectedCSVFile] = useState(data.internal.settings.path_outcome_file || "") // Selected CSV file
  const [selectedSaveFolder, setSelectedSaveFolder] = useState("") // Selected save folder
  const [selectedWSFolder, setSelectedWSFolder] = useState(data.internal.settings.path_ws_experiments || "") // Selected workspace folder
  const [listCSVFiles, setListCSVFiles] = useState([]) // List of csv files in the workspace
  const [listWSFolders, setListWSFolders] = useState([]) // List of folders in the workspace
  const [reload, setReload] = useState(false)
  const { globalData } = useContext(DataContext) // We get the global data from the context

  useEffect(() => {
    if (!data.setupParam.possibleSettings.defaultSettings.outcome_name){
      data.setupParam.possibleSettings.defaultSettings.outcome_name = data.internal.settings.outcome_name
    }
    if (data.internal.settings.method != data.setupParam.possibleSettings.defaultSettings.method){
      data.setupParam.possibleSettings.defaultSettings.method = data.internal.settings.method
    }
    if (!data.setupParam.possibleSettings.defaultSettings.path_outcome_file){
      data.setupParam.possibleSettings.defaultSettings.path_outcome_file = data.internal.settings.path_outcome_file
      setSelectedCSVFile(data.internal.settings.path_outcome_file)
    }
    if (!data.setupParam.possibleSettings.defaultSettings.path_save_experiments){
      data.setupParam.possibleSettings.defaultSettings.path_save_experiments = data.internal.settings.path_save_experiments
      setSelectedSaveFolder(data.internal.settings.path_save_experiments)
    }
    updateWSfolder()
    updateCSVFilesList()
    setReload(!reload)
  }, [])
  
  useEffect(() => {
    updateWSfolder()
    updateCSVFilesList()
  }, [globalData])

  const updateWSfolder = () => {
    if (globalData !== undefined) {
      let keys = Object.keys(globalData)
      let wsFolders = []
      keys.forEach((key) => {
        if (globalData[key].type === "directory" && !globalData[key]?.path?.includes(".medomics") && !globalData[key]?.path?.includes(".mediml")) {
          wsFolders.push({ name: globalData[key].name, value: globalData[key].path })
        }
      })
      setListWSFolders(wsFolders)
    }
  }

  const updateCSVFilesList = () => {
    if (globalData !== undefined) {
      let keys = Object.keys(globalData)
      let csvFiles = []
      keys.forEach((key) => {
        if (globalData[key].type === "csv") {
          csvFiles.push({ name: globalData[key].name, value: globalData[key].path })
        }
      })
      setListCSVFiles(csvFiles)
    }
  }

  const handleCSVFileChange = (event) => {
    var fileList = event.target.files
    if (fileList.length > 0) {
      fileList = fileList[0].path
      data.setupParam.possibleSettings.defaultSettings.path_outcome_file = fileList
    }
    else {
      data.setupParam.possibleSettings.defaultSettings.path_outcome_file = event.target.files.path
    }
    // Update node warnings
    updateHasWarning(data)
    setReload(!reload)
  }

  const handleSaveFolderChange = (event) => {
    var fileList = event.target.files
    if (fileList.length > 0) {
      fileList = fileList[0].path
      // The path of the image needs to be the path of the common folder of all the files
      // If the directory is constructed according to standard DICOM format, the path
      // of the image is the one containning the folders image and mask
      if (fileList.indexOf("\\") >= 0) {
        fileList = fileList.split("\\").slice(0, -1).join("\\")
      } else if (fileList.indexOf("/") >= 0) {
        fileList = fileList.split("/").slice(0, -1).join("/")
      } else {
        fileList = fileList.split("/").slice(0, -1).join("/")
      }
      data.setupParam.possibleSettings.defaultSettings.path_save_experiments = fileList
      data.internal.settings.path_save_experiments = fileList
    }
    else {
      data.setupParam.possibleSettings.defaultSettings.path_save_experiments = event.target.files.path
      data.internal.settings.path_save_experiments = event.target.files.path
    }
    // Update node warnings
    updateHasWarning(data)
    setReload(!reload)
  }

  return (
    <>
      <Node
        key={id}
        id={id}
        data={data}
        type={type}
        setupParam={data.setupParam}
        nodeSpecific={
          <>
            <Row 
              className="form-group-box" 
              style={{ maxHeight: "400px", overflowY: "auto", overflowX: "hidden", paddingRight: "8px" }}
            >
              <DocLink
                linkString={"https://medomicslab.gitbook.io/MEDiml-app-docs/learning"}
                name={"Learn more about the nodes"}
                image={"https://www.svgrepo.com/show/521262/warning-circle.svg"}
              />
              {/* Outcome Name */}
              <Form.Group controlId="outcomeName">
                <Form.Label className="outcomeName">Outcome Name</Form.Label>
                <p style={{fontSize: "13px", fontStyle: "italic", fontWeight: "normal", margin: "0 0 8px 0"}}>A reference name to describe the problem studied.</p>
                <InputText
                  style={{ maxWidth: "100%", height: "auto", width: "auto", display: "block", margin: "0 auto" }}
                  value={data.setupParam.possibleSettings.defaultSettings.outcome_name}
                  placeholder="Ex: RCC_Subtype"
                  onChange={(event) => {
                    data.setupParam.possibleSettings.defaultSettings.outcome_name = event.target.value
                    data.internal.settings.outcome_name = event.target.value
                    // Update node warnings
                    updateHasWarning(data)
                    setReload(!reload)
                  }}
                />
              </Form.Group>

              {/* Split Method */}
              <Form.Group controlId="splitMethod">
              <Form.Label className="splitMethod">Create Holdout Set</Form.Label>
              <p style={{fontSize: "13px", fontStyle: "italic", fontWeight: "normal", margin: "0 0 8px 0"}}>If activated a holdout set will be created. If not, all the data will be used for learning.</p>
                <InputSwitch 
                    checked={data.setupParam.possibleSettings.defaultSettings.method == 'random' ? true : false} 
                    onChange={(event) => {
                      data.setupParam.possibleSettings.defaultSettings.method = event.value ? 'random' : 'all_learn'
                      data.internal.settings.method = event.value ? 'random' : 'all_learn'
                      // Update node warnings
                      updateHasWarning(data)
                      setReload(!reload)
                    }}
                />
              </Form.Group>

              {/* Workspace Folder */}
              <Form.Group controlId="workspaceFolder">
                <Form.Label className="workspaceFolder">Experiment's Workspace Folder</Form.Label>
                <p style={{fontSize: "13px", fontStyle: "italic", fontWeight: "normal", margin: "0 0 8px 0"}}>
                  Folder containing the experiments' resources (features, outcome file, etc.).
                </p>
                <Col style={{ width: "300px", margin: "0 auto", display: "block", textAlign: "center" }}>
                  <Dropdown
                    style={{ maxWidth: "100%", height: "auto", width: "auto" }}
                    filter
                    value={selectedWSFolder}
                    onChange={(e) => {
                      data.setupParam.possibleSettings.defaultSettings.path_ws_experiments = e.value
                      data.internal.settings.path_ws_experiments = e.value
                      setSelectedWSFolder(e.value)
                      // Update node warnings
                      updateHasWarning(data)
                      setReload(!reload)
                    }}
                    options={listWSFolders}
                    optionLabel="name"
                    display="chip"
                    placeholder="Select a folder"
                  />
                </Col>
              </Form.Group>

              {/* Path Outcome */}
              <Form.Group controlId="outcomeFile">
              <Form.Label className="outcomeFile">Outcomes CSV</Form.Label>
              <p style={{fontSize: "13px", fontStyle: "italic", fontWeight: "normal", margin: "0 0 8px 0"}}>CSV file of the outcomes.</p>
              <Col style={{ width: "300px", margin: "0 auto", display: "block", textAlign: "center" }}>
                <Dropdown
                  style={{ maxWidth: "100%", height: "auto", width: "auto" }}
                  filter
                  value={selectedCSVFile}
                  onChange={(e) => {
                    data.setupParam.possibleSettings.defaultSettings.path_outcome_file = e.value
                    data.internal.settings.path_outcome_file = e.value
                    setSelectedCSVFile(e.value)
                    // Update node warnings
                    updateHasWarning(data)
                    setReload(!reload)
                  }}
                  options={listCSVFiles}
                  optionLabel="name"
                  display="chip"
                  placeholder="Select a CSV file"
                />
              </Col>
              </Form.Group>

              {/* Save Folder */}
              <Form.Group controlId="experimentSaveFolder">
                <Form.Label className="experimentSaveFolder">Save Folder</Form.Label>
                <p style={{fontSize: "13px", fontStyle: "italic", fontWeight: "normal", margin: "0 0 8px 0"}}>
                  Folder where the results will be saved. The folder should not be empty.
                </p>
                <Col style={{ width: "300px", margin: "0 auto", display: "block", textAlign: "center" }}>
                  <Dropdown
                    style={{ maxWidth: "100%", height: "auto", width: "auto" }}
                    filter
                    value={selectedSaveFolder}
                    onChange={(e) => {
                      data.setupParam.possibleSettings.defaultSettings.path_save_experiments = e.value
                      data.internal.settings.path_save_experiments = e.value
                      setSelectedSaveFolder(e.value)
                      // Update node warnings
                      updateHasWarning(data)
                      setReload(!reload)
                    }}
                    options={listWSFolders}
                    optionLabel="name"
                    display="chip"
                    placeholder="Select a folder"
                  />
                </Col>
              </Form.Group>
            </Row>
          </>
        }
      />
    </>
  )
}

export default Split
