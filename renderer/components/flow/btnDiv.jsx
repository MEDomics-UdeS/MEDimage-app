import React from "react"
import { Button } from "react-bootstrap"
import * as Icon from "react-bootstrap-icons"
import { TfiSave } from "react-icons/tfi"
import { PiDownload } from "react-icons/pi"
import { AiOutlineImport } from "react-icons/ai"
import { Tooltip } from "primereact/tooltip"

/**
 *
 * @param {List} buttonList List of buttons to display
 * @description This component is used to display a list of buttons
 * @example
 * <BtnDiv buttonsList={[{type: 'clear', onClick: () => {}, disabled: true}]}/>
 */
const BtnDiv = ({ buttonsList, op }) => {
  return (
    <>
      {buttonsList.map((button) => {
        return buttonType[button.type](button.onClick, button.disabled, op)
      })}
    </>
  )
}
export default BtnDiv

// This is the list of buttons that can be displayed
// Each button has a type and an onClick function
// You can add more buttons here
const buttonType = {
  clear: (onClear, disabled = false) => {
    return (
      <>
        <Tooltip key="clearTip" target=".clearBtn" />
        <Button key="clear" className="clearBtn" data-pr-tooltip="Clear the workflow" data-pr-position="bottom" variant="outline margin-left-10 padding-5" disabled={disabled} onClick={onClear}>
          <Icon.Trash width="30px" height="30px" />
        </Button>
      </>
    )
  },
  save: (onSave, disabled = false) => {
    return (
      <>
        <Tooltip key="saveTip" target=".saveBtn" />
        <Button
          key="save"
          className="saveBtn"
          data-pr-tooltip="Save the workflow to a json file"
          data-pr-position="bottom"
          variant="outline margin-left-10 padding-5"
          disabled={disabled}
          onClick={onSave}
        >
          <TfiSave style={{ width: "30px", height: "auto", padding: "2px" }} />
        </Button>
      </>
    )
  },
  download: (onDownload, disabled = false) => {
    return (
      <Button key="download" variant="outline margin-left-10 padding-5" onClick={onDownload} disabled={disabled}>
        <PiDownload style={{ width: "30px", height: "auto" }} />
      </Button>
    )
  },
  load: (onLoad, disabled = false) => {
    return (
      <>
        <Tooltip key="loadTip" target=".loadBtn" />
        <Button
          key="load"
          className="loadBtn"
          data-pr-tooltip="Load workflow from a json file"
          data-pr-position="bottom"
          variant="outline margin-left-10 padding-5"
          disabled={disabled}
          onClick={onLoad}
        >
          <AiOutlineImport style={{ width: "30px", height: "auto" }} />
        </Button>
      </>
    )
  },
  run: (onRun, disabled = false) => {
    return (
      <>
        <Tooltip key="runTip" target=".runBtn" />
        <Button key="run" className="runBtn" data-pr-tooltip="Run all pipelines" data-pr-position="bottom" variant="outline margin-left-10 padding-5" disabled={disabled} onClick={onRun}>
          <Icon.PlayCircle width="30px" height="30px" />
        </Button>
      </>
    )
  },
  back: (onBack, disabled = false) => {
    return (
      <Button key="back" variant="outline margin-left-10 padding-5" onClick={onBack} disabled={disabled}>
        <Icon.Backspace width="30px" height="30px" />
      </Button>
    )
  },
  export: (onExport, disabled = false, op) => {
    return (
      <>
        <Tooltip key="exportTip" target=".saveBtn" />
        <Button
          key="export"
          className="saveBtn"
          data-pr-tooltip="Export settings for batch extraction"
          data-pr-position="bottom"
          variant="outline margin-left-10 padding-5"
          disabled={disabled}
          onClick={(e) => {
            onExport
            op.current.toggle(e)
          }}
        >
          <i className="pi pi-file-export" style={{ fontSize: "1.8rem" }}></i>
        </Button>
      </>
    )
  },
  loadDeafult: (onLoadDeafult) => {
    return (
      <>
        <Tooltip key="loadDeafultTip" target=".loadDeafultBtn" />
        <Button
          key="loadDeafult"
          className="loadDeafultBtn"
          data-pr-tooltip="Load default learning workflow"
          data-pr-position="left"
          variant="outline-info uccess margin-left-10 padding-5"
          onClick={onLoadDeafult}
        >
          <AiOutlineImport style={{ width: "30px", height: "auto" }} />
        </Button>
      </>
    )
  }
}