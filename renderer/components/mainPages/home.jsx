import React, { useContext, useEffect, useState } from "react"
import Image from "next/image"
import myimage from "../../../resources/medomics_transparent_bg.png"
import { Button, Stack } from "react-bootstrap"
import { WorkspaceContext } from "../workspace/workspaceContext"
import { ipcRenderer } from "electron"
import FirstSetupModal from "../generalPurpose/installation/firstSetupModal"

/**
 *
 * @returns the home page component
 */
const HomePage = () => {
  const { workspace, setWorkspace, recentWorkspaces } = useContext(WorkspaceContext)
  const [hasBeenSet, setHasBeenSet] = useState(workspace.hasBeenSet)
  const [appVersion, setAppVersion] = useState("")
  const [requirementsMet, setRequirementsMet] = useState(true)

  async function handleWorkspaceChange() {
    ipcRenderer.send("messageFromNext", "requestDialogFolder")
  }

  // Check if the requirements are met
  useEffect(() => {
    ipcRenderer.invoke("checkRequirements").then((data) => {
      console.log("Requirements: ", data)
      if (data.pythonInstalled && data.mongoDBInstalled) {
        setRequirementsMet(true)
      } else {
        setRequirementsMet(false)
      }
    })
  }, [])

  // We set the workspace hasBeenSet state
  useEffect(() => {
    if (workspace.hasBeenSet == false) {
      setHasBeenSet(true)
    } else {
      setHasBeenSet(false)
    }
  }, [workspace])

  // Get app's version
  useEffect(() => {
    ipcRenderer.invoke("getAppVersion").then((data) => {
      setAppVersion(data)
    })
  }, [])

  // We set the recent workspaces -> We send a message to the main process to get the recent workspaces, the workspace context will be updated by the main process in _app.js
  useEffect(() => {
    ipcRenderer.send("messageFromNext", "getRecentWorkspaces")
  }, [])

  return (
    <>
      <div 
        className="container"
        style={{
          paddingTop: "1rem",
          display: "flex",
          flexDirection: "column",
          overflowY: "auto",
          scrollbarColor: "#b0b0b0 #f5f5f5"
        }}
      >
        <Stack direction="vertical" gap={1} style={{ alignContent: "center", flexGrow: 1 }}>
          <h2>Home page</h2>
          <Stack direction="horizontal" gap={0} style={{ padding: "0 0 0 0", alignContent: "center" }}>
            <h1 style={{ fontSize: "5rem" }}>MEDiml</h1>
            <h2 style={{ fontSize: "2rem", marginTop: "2.5rem" }}>v{appVersion}</h2>
            <Image src={myimage} alt="" style={{ height: "175px", width: "175px" }} />
          </Stack>
          {hasBeenSet ? (
            <>
              <h5>Set up your workspace to get started</h5>
              <Button onClick={handleWorkspaceChange} style={{ margin: "1rem" }}>
                Set Workspace
              </Button>
              <h5>Or open a recent workspace</h5>
              <Stack direction="vertical" gap={0} style={{ padding: "0 0 0 0", alignContent: "center" }}>
                {recentWorkspaces.map((workspace, index) => {
                  if (index > 4) return
                  return (
                    <a
                      key={index}
                      onClick={() => {
                        ipcRenderer.invoke("setWorkingDirectory", workspace.path).then((data) => {
                          if (workspace !== data) {
                            let workspaceToSet = { ...data }
                            setWorkspace(workspaceToSet)
                          }
                        })
                      }}
                      style={{ margin: "0rem", color: "var(--blue-600)" }}
                    >
                      <h6>{workspace.path}</h6>
                    </a>
                  )
                })}
              </Stack>
            </>
          ) : (
            <h5>Workspace is set to {workspace.workingDirectory.path}</h5>
          )}
        </Stack>

        {/* Getting Started Section (Full Width) */}
        <div
          style={{
            marginTop: "2rem",
            padding: "2rem",
            borderRadius: "8px",
            boxShadow: "0px 2px 5px rgba(128, 117, 117, 0.1)",
            textAlign: "left",
            width: "100%",
          }}
        >
          <h3 style={{ marginBottom: "1rem", color: "#4991dfff" }}>
            Getting Started 🚀
          </h3>
          
          <p>
          To effectively navigate MEDiml and its functionalities, we recommend consulting the official documentation and tutorial resources.
          These materials will help you understand how to analyze medical images using MEDiml, define and run experimentations, and evaluate machine learning models.
          </p>

          <p>We provide dedicated tutorials and documentation to guide you step by step:</p>

          <ul style={{ paddingLeft: "1.5rem", listStyleType: "none" }}>
            <li>📖  
              <a href="https://medomicslab.gitbook.io/mediml-app-docs/" 
                  target="_blank" rel="noopener noreferrer" style={{ color: "#4991dfff", textDecoration: "none", marginLeft: "5px" }}>
                MEDiml Documentation
              </a>
            </li>

            <li>🎥 
              <a href="https://youtube.com/playlist?list=PLEPy2VhC4-D5Eg-UxRyTtmUZRh-D5m_Ru&si=n9lX4lRYfDci3v5V" 
                  target="_blank" rel="noopener noreferrer" style={{ color: "#4991dfff", textDecoration: "none", marginLeft: "5px" }}>
                Video Tutorials
              </a>
            </li>
            </ul>

            {/* Warning section */}
            <div 
            style={{
              marginTop: "1rem",
              padding: "1rem",
              backgroundColor: "#97781bff",
              borderLeft: "4px solid #ffc107",
              borderRadius: "5px"
            }}
          >
            ⚠️ MEDiml is part of the MEDomics platform, and only supports medical image analysis. 
            To access other types of data analysis, please refer <a href="https://medomics.app/" 
                  target="_blank" rel="noopener noreferrer" style={{ color: "#4991dfff", textDecoration: "none", marginLeft: "5px" }}>
                here
              </a>.
          </div>
        </div>
      </div>  
      {!requirementsMet && process.platform !=="darwin" && <FirstSetupModal visible={!requirementsMet} closable={false} setRequirementsMet={setRequirementsMet} />}
    </>
  )
}

export default HomePage
