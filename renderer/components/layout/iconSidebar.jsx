/* eslint-disable no-unused-vars */
import { ipcRenderer } from "electron"
import { Tooltip } from "primereact/tooltip"
import { useContext, useEffect, useState } from "react"
import { NavDropdown } from "react-bootstrap"
import { Gear, HouseFill } from "react-bootstrap-icons"
import Nav from "react-bootstrap/Nav"
import { FaBriefcase, FaLayerGroup } from "react-icons/fa"
import { FaHeadSideVirus } from "react-icons/fa6"
import { GiDigDug } from "react-icons/gi"
import { WorkspaceContext } from "../workspace/workspaceContext"
import { LayoutModelContext } from "./layoutContext"
import { Briefcase, Layers, Star, Target } from "lucide-react"


/**
 * @description Sidebar component containing icons for each page
 * @param {function} onSidebarItemSelect - function to handle sidebar item selection
 * @returns Returns the sidebar component with icons for each page
 */
const IconSidebar = ({ onSidebarItemSelect }) => {
  // eslint-disable-next-line no-unused-vars
  const { dispatchLayout, developerMode, setDeveloperMode } = useContext(LayoutModelContext)
  const { workspace } = useContext(WorkspaceContext)
  const [appVersion, setAppVersion] = useState("")
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

    // Get app's version
    ipcRenderer.invoke("getAppVersion").then((data) => {
      setAppVersion(data.replace(/v/, ""))
    })
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

  /**
   *
   * @param {Event} event
   * @param {string} name
   */
  function handleDoubleClickLanding(event, name) {
    event.stopPropagation()
    console.log(`Double clicked ${name}`, event, `open${name}LandingPage`)
    dispatchLayout({ type: `open${name}LandingPage`, payload: { pageId: name } })
  }

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
        <Tooltip target=".ExtMEDimgNav" {...delayOptions} className="tooltip-icon-sidebar" />
        <Tooltip target=".BatchExtractorNav" {...delayOptions} className="tooltip-icon-sidebar" />
        <Tooltip target=".DataManagerNav" {...delayOptions} className="tooltip-icon-sidebar" />
        {/* ------------------------------------------- END Tooltips ----------------------------------------- */}

        {/* ------------------------------------------- ICON NAVBAR ----------------------------------------- */}

        <Nav defaultActiveKey="/home" className="flex-column" style={{ width: "100%", height: "100%" }}>
          <Nav.Link
            className={`homeNavIcon btnSidebar`}
            data-pr-at="right center"
            data-pr-tooltip="Home"
            data-pr-my="left center"
            href="#home"
            eventKey="home"
            data-tooltip-id="tooltip-home"
            onClick={(event) => handleClick(event, "home")}
            onDoubleClick={(event) => handleDoubleClick(event, "Home")}
          >
            <HouseFill size={"1.25rem"} width={"100%"} height={"100%"} />
          </Nav.Link>
          
          <NavDropdown.Divider style={{ height: "3rem" }} />

          <div className="medomics-layer">
            <div className="sidebar-icons">
                {/* MEDiml Extraction Module */}
                <Nav.Link
                  className={`ExtMEDimgNav btnSidebar align-center`}
                  data-pr-at="right center"
                  data-pr-my="left center"
                  data-pr-tooltip="MEDiml Modules"
                  data-is-ext-btn
                  onClick={(event) => {
                    event.stopPropagation()
                    event.preventDefault()
                    handleDoubleClickLanding(event, "Modules")
                    setExtractionBtnstate(!extractionBtnstate)
                  }}
                  onDoubleClick={(event) => handleDoubleClickLanding(event, "Modules")}
                >
                  <Target style={{ height: "1.5rem", width: "auto" }} />
                </Nav.Link>
            </div>
          </div>
          <div className="medomics-layer">
            <div className="sidebar-icons">
              {/* DataManager */}
              <Nav.Link
                className={`DataManagerNav btnSidebar align-center`}
                icon="pi pi-book"
                data-pr-at="right center"
                data-pr-my="left center"
                data-pr-tooltip="DataManager"
                data-is-ext-btn
                onClick={(event) => {
                  event.stopPropagation()
                  event.preventDefault()
                  handleDoubleClick(event, "DataManager")
                  // handleClick(event, "extractionMEDiml")
                  setExtractionBtnstate(!extractionBtnstate)
                }}
                onDoubleClick={(event) => handleDoubleClick(event, "DataManager")}
              >
                <Briefcase style={{ height: "1.5rem", width: "auto" }} />
              </Nav.Link>
            </div>
          </div>
          <div className="medomics-layer">
            <div className="sidebar-icons">
              {/* BatchExtractor */}
              <Nav.Link
                className={`BatchExtractorNav btnSidebar align-center`}
                data-pr-at="right center"
                data-pr-my="left center"
                data-pr-tooltip="BatchExtractor"
                data-is-ext-btn
                onClick={(event) => {
                  event.stopPropagation()
                  event.preventDefault()
                  handleDoubleClick(event, "BatchExtractor")
                  setExtractionBtnstate(!extractionBtnstate)
                }}
                onDoubleClick={(event) => handleDoubleClick(event, "BatchExtractor")}
              >
                <Layers style={{ height: "1.5rem", width: "auto" }} />
              </Nav.Link>
            </div>
          </div>
          <NavDropdown.Divider style={{ height: "3rem" }} />

          {/* div that puts the buttons to the bottom of the sidebar*/}
          <div className="d-flex icon-sidebar-divider" style={{ flexGrow: "1" }}></div>

          <div className="sidebar-version">v{appVersion}</div>

          <Nav.Link
            className={`settingsNav btnSidebar`}
            data-pr-at="right center"
            data-pr-my="left center"
            data-pr-tooltip="Settings"
            eventKey="settings"
            data-tooltip-id="tooltip-settings"
            onClick={() => dispatchLayout({ type: `openSettings`, payload: { pageId: "Settings" } })}
            disabled={disabledIcon}
          >
            <Gear size={"1.5rem"} />
          </Nav.Link>
        </Nav>
        {/* ------------------------------------------- END ICON NAVBAR ----------------------------------------- */}
      </div>
    </>
  )
}

export default IconSidebar
