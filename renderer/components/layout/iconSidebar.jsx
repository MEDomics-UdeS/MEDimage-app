/* eslint-disable no-unused-vars */
import { Button } from "primereact/button"
import { Tooltip } from "primereact/tooltip"
import React, { useContext, useEffect, useState } from "react"
import { NavDropdown } from "react-bootstrap"
import { Gear, HouseFill } from "react-bootstrap-icons"
import Nav from "react-bootstrap/Nav"
import { FaHeadSideVirus } from "react-icons/fa6"
import { TbFileExport } from "react-icons/tb"
import { VscChromeClose } from "react-icons/vsc"
import { WorkspaceContext } from "../workspace/workspaceContext"
import { LayoutModelContext } from "./layoutContext"

/**
 * @description Sidebar component containing icons for each page
 * @param {function} onSidebarItemSelect - function to handle sidebar item selection
 * @returns Returns the sidebar component with icons for each page
 */
const IconSidebar = ({ onSidebarItemSelect }) => {
  // eslint-disable-next-line no-unused-vars
  const { dispatchLayout, developerMode, setDeveloperMode } = useContext(LayoutModelContext)
  const [activeKey, setActiveKey] = useState("home") // activeKey is the name of the page
  const [disabledIcon, setDisabledIcon] = useState("disabled") // disabled is the state of the page
  const [developerModeNav, setDeveloperModeNav] = useState(true)
  const [extractionBtnstate, setExtractionBtnstate] = useState(false)
  const [buttonClass, setButtonClass] = useState("")

  const delayOptions = { showDelay: 750, hideDelay: 0 }

  // default action to set developer mode to true
  useEffect(() => {
    setDeveloperMode(true)
    setDeveloperModeNav(true)
  }, [])

  /**
   * @description Toggles the developer mode
   */
  function handleToggleDeveloperMode() {
    console.log("handleToggleDeveloperMode")
    setDeveloperMode(!developerMode)
    setDeveloperModeNav(!developerModeNav)
  }

  /**
   *
   * @param {Event} event
   * @param {string} name
   */
  function handleDoubleClick(event, name) {
    event.stopPropagation()
    console.log(`Double clicked ${name}`, event, `open${name}Module`)
    dispatchLayout({ type: `open${name}Module`, payload: { pageId: name } })
  }

  const { workspace } = useContext(WorkspaceContext)

  /**
   * @description Sets the active key and disabled state of the sidebar icons
   */
  useEffect(() => {
    if (!workspace.hasBeenSet) {
      setActiveKey("home")
      setDisabledIcon(true)
    } else {
      setDisabledIcon(false)
    }
  }, [workspace])

  useEffect(() => {}, [extractionBtnstate])

  /**
   *
   * @param {Event} event The event that triggered the click
   * @param {string} name The name of the page
   */
  function handleClick(event, name) {
    onSidebarItemSelect(name)
    console.log(`clicked ${name}`, event)
    setActiveKey(name)
  }

  /**
   * @description Handles the click on the settings button
   */
  const handleNavClick = () => {
    setButtonClass(buttonClass === "" ? "show" : "")
  }

  return (
    <>
      <div className="icon-sidebar">
        {/* ------------------------------------------- Tooltips ----------------------------------------- */}
        <Tooltip target=".homeNavIcon" {...delayOptions} className="tooltip-icon-sidebar" />
        <Tooltip target=".explorerNav" {...delayOptions} className="tooltip-icon-sidebar" />
        <Tooltip target=".inputNav" {...delayOptions} className="tooltip-icon-sidebar" />
        <Tooltip target=".extractionNav" {...delayOptions} className="tooltip-icon-sidebar" data-pr-disabled={extractionBtnstate} />
        <Tooltip target=".classificationNav" {...delayOptions} className="tooltip-icon-sidebar" />
        <Tooltip target=".exploratoryNav" {...delayOptions} className="tooltip-icon-sidebar" />
        <Tooltip target=".learningNav" {...delayOptions} className="tooltip-icon-sidebar" />
        <Tooltip target=".resultsNav" {...delayOptions} className="tooltip-icon-sidebar" />
        <Tooltip target=".evaluationNav" {...delayOptions} className="tooltip-icon-sidebar" />
        <Tooltip target=".applicationNav" {...delayOptions} className="tooltip-icon-sidebar" />
        <Tooltip target=".ext-MEDimg-btn" {...delayOptions} className="tooltip-icon-sidebar" />
        <Tooltip target=".ext-text-btn" {...delayOptions} className="tooltip-icon-sidebar" />
        <Tooltip target=".ext-ts-btn" {...delayOptions} className="tooltip-icon-sidebar" />
        <Tooltip target=".ext-img-btn" {...delayOptions} className="tooltip-icon-sidebar" />

        {/* ------------------------------------------- END Tooltips ----------------------------------------- */}

        {/* ------------------------------------------- ICON NAVBAR ----------------------------------------- */}

        <Nav defaultActiveKey="/home" className="flex-column" style={{ width: "100%", height: "100%" }}>
          <Nav.Link className="homeNavIcon btnSidebar" data-pr-at="right center" data-pr-tooltip="Home" data-pr-my="left center" href="#home" eventKey="home" data-tooltip-id="tooltip-home" onClick={(event) => handleClick(event, "home")} onDoubleClick={(event) => handleDoubleClick(event, "Home")}>
            <HouseFill size={"1.25rem"} width={"100%"} height={"100%"} style={{ scale: "0.65" }} />
          </Nav.Link>

          <NavDropdown.Divider className="icon-sidebar-divider" style={{ height: "6rem" }} />

          <div className="medomics-layer design">
            <div className="sidebar-icons">

              <Nav.Link
                className="extractionNav btnSidebar align-center"
                data-pr-at="right center"
                data-pr-my="left center"
                data-pr-tooltip="extraction"
                data-pr-disabled={extractionBtnstate}
                eventKey="extraction"
                data-tooltip-id="tooltip-extraction"
                onDoubleClick={(event) => handleDoubleClick(event, "extraction")}
                onClick={() => {
                  setExtractionBtnstate(!extractionBtnstate)
                }}
                disabled={disabledIcon}
                onBlur={(event) => {
                  let clickedTarget = event.relatedTarget
                  let blurAccepeted = true
                  if (clickedTarget) {
                    blurAccepeted = !clickedTarget.getAttribute("data-is-ext-btn")
                  } else {
                    blurAccepeted = true
                  }
                  blurAccepeted && setExtractionBtnstate(false)
                }}
              >
                {extractionBtnstate ? <VscChromeClose style={{ height: "1.7rem", width: "auto" }} /> : <TbFileExport style={{ height: "1.7rem", width: "auto" }} />}
                <div className={`btn-group-ext ${extractionBtnstate ? "clicked" : ""}`}>
                  <Button
                    className="DataManager-btn"
                    icon="pi pi-book"
                    data-pr-at="right center"
                    data-pr-my="left center"
                    data-pr-tooltip="DataManager"
                    data-is-ext-btn
                    onClick={(event) => {
                      event.stopPropagation()
                      event.preventDefault()
                      handleDoubleClick(event, "DataManager")
                      // handleClick(event, "extractionMEDimage")
                      setExtractionBtnstate(!extractionBtnstate)
                    }}
                    onDoubleClick={(event) => handleDoubleClick(event, "ExtractionMEDimage")}
                  />
                  <Button
                    className="ext-MEDimg-btn"
                    icon="pi pi-image"
                    data-pr-at="right center"
                    data-pr-my="left center"
                    data-pr-tooltip="Single scan"
                    data-is-ext-btn
                    onClick={(event) => {
                      event.stopPropagation()
                      event.preventDefault()
                      handleDoubleClick(event, "ExtractionMEDimage")
                      // handleClick(event, "extractionMEDimage")
                      setExtractionBtnstate(!extractionBtnstate)
                    }}
                    onDoubleClick={(event) => handleDoubleClick(event, "ExtractionMEDimage")}
                  />
                  <Button
                    className="BatchExtractor-btn"
                    icon="pi pi-list"
                    data-pr-at="right center"
                    data-pr-my="left center"
                    data-pr-tooltip="BatchExtractor"
                    data-is-ext-btn
                    onClick={(event) => {
                      event.stopPropagation()
                      event.preventDefault()
                      handleDoubleClick(event, "BatchExtractor")
                      // handleClick(event, "extractionMEDimage")
                      setExtractionBtnstate(!extractionBtnstate)
                    }}
                    onDoubleClick={(event) => handleDoubleClick(event, "ExtractionMEDimage")}
                  />
                </div>
              </Nav.Link>

              <Nav.Link 
                className="classificationNav btnSidebar align-center" 
                data-pr-at="right center" 
                data-pr-my="left center" 
                data-pr-tooltip="learning"
                data-pr-disabled={extractionBtnstate} 
                eventKey="learning" 
                data-tooltip-id="tooltip-learning"
                onDoubleClick={(event) => handleDoubleClick(event, "LearningMEDimage")} 
                onClick={(event) => handleDoubleClick(event, "LearningMEDimage")} 
                disabled={disabledIcon}
                >
                {" "}
                <FaHeadSideVirus style={{ height: "1.7rem", width: "auto" }} />
              </Nav.Link>

            </div>
            <div className="medomics-layer-text">MEDimage</div>
          </div>
          <NavDropdown.Divider style={{ height: "3rem" }} />

          <NavDropdown.Divider style={{ height: "3rem" }} />

          {/* div that puts the buttons to the bottom of the sidebar*/}
          <div className="d-flex icon-sidebar-divider" style={{ flexGrow: "1" }}></div>

          {/* ------------------------------------------- SETTINGS BUTTON ----------------------------------------- */}
          <Nav.Link className="settingsNav btnSidebar" data-pr-at="right center" data-pr-my="left center" data-pr-tooltip="Settings" eventKey="settings" data-tooltip-id="tooltip-settings" onClick={() => dispatchLayout({ type: `openSettings`, payload: { pageId: "Settings" } })} disabled={disabledIcon}>
            <Gear size={"1.25rem"} width={"100%"} height={"100%"} style={{ scale: "0.65" }} />
          </Nav.Link>
        </Nav>
        {/* ------------------------------------------- END ICON NAVBAR ----------------------------------------- */}
      </div>
    </>
  )
}

export default IconSidebar
