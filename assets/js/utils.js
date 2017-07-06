
export function getClassForStatus(status) {
  switch(status) {
    case 'fail':
    case 'error':
      return 'slds-truncate slds-badge slds-theme--error'
    case 'success':
      return 'slds-truncate slds-badge slds-theme--success'
  }
}
