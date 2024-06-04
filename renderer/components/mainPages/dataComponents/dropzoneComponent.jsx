import React, { useCallback, useState, useContext, useMemo } from "react"
import { useDropzone } from "react-dropzone"
import fs from "fs"
import { WorkspaceContext } from "../../workspace/workspaceContext"
import MedDataObject from "../../workspace/medDataObject"
import { toast } from "react-toastify"

/**
 * @typedef {React.FunctionComponent} DropzoneComponent
 * @description This component is the dropzone component that will be used to upload files to the workspace.
 * @params {Object} children - The children of the component
 * @summary This component is used to upload files to the workspace. It is used in the InputSidebar.
 * @todo Add the functionality to upload more file types than just CSV files
 */
export default function DropzoneComponent({ children, item = undefined, ...props }) {
  // eslint-disable-next-line no-unused-vars
  const [uploadedFile, setUploadedFile] = useState(null)
  // eslint-disable-next-line no-unused-vars
  const [uploadProgress, setUploadProgress] = useState(0)

  const { workspace } = useContext(WorkspaceContext)

  let directoryPath = `${workspace.workingDirectory.path}/DATA`
  if (item !== undefined) {
    if (item.path !== undefined) {
      directoryPath = item.path
    }
  }

  const onDrop = useCallback((acceptedFiles, fileRejections, event) => {
    console.log("event", event)
    event.stopPropagation()
    const reader = new FileReader()

    reader.onabort = () => console.log("file reading was aborted")
    reader.onerror = () => console.log("file reading failed")
    reader.onload = () => {
      acceptedFiles.forEach((file) => {
        console.log("file", file)
        fs.copyFile(file.path, `${directoryPath}/${file["name"]}`, (err) => {
          if (err) {
            console.error("Error copying file:", err)
          } else {
            console.log("File copied successfully")
          }
        })
      })
    }

    // read file contents
    acceptedFiles.forEach((file) => {
      reader.readAsBinaryString(file)
      MedDataObject.updateWorkspaceDataObject()
    })
  }, [])

  let acceptedFiles = undefined
  if (item !== undefined) {
    if (item.acceptedFiles !== undefined) {
      acceptedFiles = item.acceptedFiles
    }
  }

  /**
   * @description - This is the useDropzone hook that is used to create the dropzone component
   * @param {Object} onDrop - The function to be executed when a file is dropped in the dropzone
   * @param {Object} onDropRejected - The function to be executed when a file is dropped in the dropzone but is rejected
   * @param {Object} noClick - A boolean that indicates if the dropzone should not be clickable
   * @param {Object} accept - The file types that are accepted by the dropzone
   * @returns {JSX.Element}
   * @see SidebarDirectoryTreeControlled - "../../layout/sidebarTools/sidebarDirectoryTreeControlled.jsx" This component is used in the SidebarDirectoryTreeControlled component
   */
  const { getRootProps, getInputProps, isFocused, isDragAccept, isDragReject } = useDropzone({
    onDrop,
    onDropRejected: useCallback((fileRejections) => {
      console.log("fileRejections", fileRejections)
      toast.error("Error: File type not accepted in this folder")
    }, []),
    noClick: props.noClick || false,
    accept: acceptedFiles ? acceptedFiles : undefined
  })

  // The style changes if the dropzone is focused, if the file is accepted or if the file is rejected
  const baseStyle = {
    display: "block",
    position: "relative",
    width: "100%",
    height: "100%",
    borderWidth: "0px"
  }

  const focusedStyle = {}

  const acceptStyle = {
    borderWidth: "2px",
    borderColor: "#00e676"
  }

  const rejectStyle = {
    borderWidth: "2px",
    borderColor: "#ff1744"
  }

  const style = useMemo(
    () => ({
      ...baseStyle,
      ...(isFocused ? focusedStyle : {}),
      ...(isDragAccept ? acceptStyle : {}),
      ...(isDragReject ? rejectStyle : {})
    }),
    [isFocused, isDragAccept, isDragReject]
  )

  return (
    <div style={{ display: "block" }}>
      <div className="directory-tree-dropzone" {...getRootProps({ style })}>
        <input {...getInputProps()} />
        {children}
      </div>
    </div>
  )
}
