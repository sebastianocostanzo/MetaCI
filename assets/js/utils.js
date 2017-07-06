
export function getClassForStatus(status) {
  switch(status) {
    case 'fail':
    case 'error':
      return 'slds-theme--error'
    case 'success':
      return 'slds-theme--success'
  }
}
