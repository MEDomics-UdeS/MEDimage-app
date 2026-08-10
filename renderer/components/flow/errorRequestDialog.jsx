import { Button } from "primereact/button"
import { Dialog } from "primereact/dialog"
import { useContext } from "react"
import { Col, Row } from "react-bootstrap"
import { toast } from "react-toastify"
import { ErrorRequestContext } from "../generalPurpose/errorRequestContext"

/**
 *
 * @returns {JSX.Element}
 * This component is used to display the error dialog when an error occurs during the execution of the flow
 *
 * To use:
 * 1. Import the ErrorRequestContext in the component
 * 2. Use the context member setError to set the error
 */
const ErrorRequestDialog = () => {
  const { error, showError, setShowError } = useContext(ErrorRequestContext)

  // Helper to extract the string message safely
  const getErrorMessage = () => {
    // If error.message is a string, use it. If it's an object with a message property, use that.
    let parsedError = error
    if (typeof error === 'string') {
      try {
        parsedError = JSON.parse(error)
        let msg = typeof parsedError?.message === 'string' 
          ? parsedError.message 
          : parsedError?.message?.message
        return msg || "An unknown error occurred"
      } catch (e) {
        // If parsing fails, treat the original string as the message
        return error
      }
    }

    const msg = typeof parsedError?.message === 'string' 
      ? parsedError.message 
      : parsedError?.message?.message
    
    return msg || "An unknown error occurred"
  }

  const displayMessage = getErrorMessage()

  return (
    <>
      <Dialog
        header="Error occurred during execution"
        visible={showError}
        style={{ width: "70vw" }}
        onHide={() => setShowError(false)}
        footer={
          <div>
            <Button label="Ok" icon="pi pi-check" onClick={() => setShowError(false)} autoFocus />
          </div>
        }
      >
        <Row className="error-dialog-header">
          <Col md="auto">
            {/* Safe access with optional chaining and fallback */}
            <h5>
              {displayMessage.charAt(0).toUpperCase() + displayMessage.slice(1)}
            </h5>
          </Col>
          <Col>
            <Button
              icon="pi pi-copy"
              rounded
              text
              severity="secondary"
              onClick={() => {
                navigator.clipboard.writeText(displayMessage)
                toast.success("Copied to clipboard")
              }}
            />
          </Col>
        </Row>
        {/* Axios error stack is usually in error.message.stack or error.stack_trace */}
        <pre className="mt-3" style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
          {
            error?.message?.stack || error?.stack_trace || "No stack trace available"
          }
        </pre>
      </Dialog>
    </>
  )
}

export default ErrorRequestDialog
